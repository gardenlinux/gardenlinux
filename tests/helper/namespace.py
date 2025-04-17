import shlex
import logging
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class NamespaceSession:
    def __init__(self, client, packages):
        self.client = client
        self.packages = packages
        self.script_path = f"/var/tmp/ns_test_script_{uuid.uuid4().hex}.sh"
        self.commands = []

    def __enter__(self):
        return self

    def run(self, cmd):
        self.commands.append(cmd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pkg_str = " ".join(shlex.quote(pkg) for pkg in self.packages)

        script_lines = [
            "#!/bin/bash",
            "set -eux",
            "",
            "mount --make-rprivate /",
            "",
            "mkdir -p /mnt/tmp_usr /mnt/tmp_etc",
            "mount -t tmpfs tmpfs /mnt/tmp_usr",
            "mount -t tmpfs tmpfs /mnt/tmp_etc",
            "",
            "cp -aT /usr /mnt/tmp_usr",
            "cp -aT /etc /mnt/tmp_etc",
            "",
            "mount --bind /mnt/tmp_usr /usr",
            "mount --bind /mnt/tmp_etc /etc",
            "",
            "apt-get update",
            f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg_str}",
        ]

        # Add user-provided commands
        script_lines += self.commands

        script = "\n".join(script_lines)
        quoted_script = shlex.quote(script)

        # Upload script
        (code, _, err) = self.client.execute_command(
            f"echo {quoted_script} > {self.script_path}", quiet=True
        )
        assert code == 0, f"Failed to upload script: {err}"

        # Make it executable
        self.client.execute_command(f"chmod +x {self.script_path}", quiet=True)

        # Run inside new mount namespace
        run_cmd = (
            f"unshare --mount --uts --ipc --pid --fork --mount-proc {self.script_path}"
        )
        (code, _, err) = self.client.execute_command(run_cmd, quiet=True)
        assert code == 0, f"Namespace script failed:\n{err}"

        # Cleanup
        self.client.execute_command(f"rm -f {self.script_path}", quiet=True)
