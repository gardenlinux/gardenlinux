import shlex
import logging
import uuid
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class NamespaceSession:
    def __init__(self, client, packages=None, timeout=20):
        self.client = client
        self.packages = packages or []
        self.id = uuid.uuid4().hex[:8]
        self.fifo = f"/tmp/ns_cmd_{self.id}.fifo"
        self.log = f"/tmp/ns_log_{self.id}.log"
        self.ready = f"/tmp/ns_ready_{self.id}.flag"
        self.runner = f"/tmp/ns_runner_{self.id}.sh"
        self.timeout = timeout

    def __enter__(self):
        logger.info(f"Starting namespace session with ID: {self.id}")
        self._cleanup_stale()
        self._prepare_fifo_and_log()
        self._upload_runner()
        self._start_runner_namespace()
        self._wait_for_ready()
        logger.info("Runner script is ready")
        return self

    def run(self, cmd):
        call_id = uuid.uuid4().hex
        self._send_to_fifo(call_id, cmd)
        self._await_end_marker(call_id)
        return self._collect_output(call_id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"Exiting namespace session with ID: {self.id}")
        self._exec(f"echo __EXIT__ > {self.fifo}")
        self._exec(f"rm -f {self.fifo} {self.log} {self.ready} {self.runner}")

    def _cleanup_stale(self):
        logger.info("Cleaning up stale files")
        self._exec(f"rm -f {self.fifo} {self.log} {self.ready} {self.runner} || true")

    def _prepare_fifo_and_log(self):
        self._exec(f"mkfifo {self.fifo}")
        self._exec(f"touch {self.log}")

    def _upload_runner(self):
        pkg_install = " ".join(shlex.quote(p) for p in self.packages)
        runner_sh = self._build_runner_script(pkg_install)
        here_doc = "\n".join(
            ["cat << 'EOF' > " + self.runner] + runner_sh.splitlines() + ["EOF"]
        )
        self._exec(here_doc)
        self._exec(f"chmod +x {self.runner}")

    def _build_runner_script(self, pkg_install):
        return """
#!/bin/bash
set -eu
mount --make-rprivate /
mkdir -p /mnt/tmp_usr /mnt/tmp_etc
mount -t tmpfs tmpfs /mnt/tmp_usr
mount -t tmpfs tmpfs /mnt/tmp_etc
cp -aT /usr /mnt/tmp_usr
cp -aT /etc /mnt/tmp_etc
mount --bind /mnt/tmp_usr /usr
mount --bind /mnt/tmp_etc /etc
(
exec 3<> "{fifo}"
  while read -r line <&3; do
    id=${{line%%:*}}; cmd=${{line#*:}}
    [[ "$cmd" == "__EXIT__" ]] && break
    out=$(eval "$cmd" 2>&1); rc=$?
    {{
      echo "==BEGIN==$id"
      echo "$out"
      echo "EXIT==$id==$rc"
      echo "==END==$id"
    }} >>"{log}"
  done
exec 3>&-
) &
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y {pkgs}
touch "{ready}"
wait
""".format(fifo=self.fifo, log=self.log, ready=self.ready, pkgs=pkg_install)

    def _start_runner_namespace(self):
        # launch runner under its own unshare namespace
        cmd = (
            f"nohup unshare --mount --uts --ipc --pid --fork --mount-proc "
            f"bash {self.runner} >/dev/null 2>&1 &"
        )
        self._exec(cmd)

    def _wait_for_ready(self):
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            ec, _, _ = self.client.execute_command(f"test -f {self.ready}", quiet=True)
            if ec == 0:
                return
            time.sleep(0.1)
        raise TimeoutError("Namespace did not become ready")

    def _send_to_fifo(self, call_id, cmd):
        line = f"{call_id}:{cmd}"
        logger.info(f"sending to fifo: {line}")
        self._exec(f"echo {shlex.quote(line)} > {self.fifo}")

    def _await_end_marker(self, call_id):
        deadline = time.time() + self.timeout
        marker = f"==END=={call_id}"
        while time.time() < deadline:
            ec, _, _ = self.client.execute_command(
                f"grep -q {shlex.quote(marker)} {self.log}", quiet=True
            )
            if ec == 0:
                return
            time.sleep(0.05)
        raise TimeoutError(f"Namespace command timed out waiting for {marker}")

    def _collect_output(self, call_id):
        logger.info(f"collecting output for call_id: {call_id}")
        ec, raw, _ = self.client.execute_command(
            f"awk '/==BEGIN=={call_id}/,/==END=={call_id}/' {self.log}", quiet=True
        )
        lines = raw.splitlines()
        exit_line = next(l for l in lines if l.startswith(f"EXIT=={call_id}=="))
        exit_code = int(exit_line.rsplit("==", 1)[1])
        start = lines.index(f"==BEGIN=={call_id}") + 1
        end = lines.index(exit_line)
        output = "\n".join(lines[start:end])
        logger.info(f"output: {output}")
        logger.info(f"exit_code: {exit_code}")
        return output, exit_code

    def _exec(self, bash_cmd):
        logger.info(f"_exec: {bash_cmd}")
        wrapped = f"bash -c {shlex.quote(bash_cmd)}"
        ec, out, err = self.client.execute_command(wrapped, quiet=True)
        assert ec == 0, f"[NamespaceSession] `{bash_cmd}` failed:\n{err}"
        return out
