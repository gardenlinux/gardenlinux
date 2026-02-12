import http.server
import json
import queue
import socketserver
import subprocess
import threading
import time
import urllib.request

# TODO: make constants configurable with cmdline args
BASE_URL = "http://10.0.2.2:8123"
SRC_DIR = "/home/ignis/src/KUBERMATIC/gardenlinux/tests"
DEST_DIR = "/run/gardenlinux-tests/tests"
TESTS_RUNNER = "/run/gardenlinux-tests/run_tests"

sync_queue = queue.Queue()


class NotifyHandler(http.server.BaseHTTPRequestHandler):
    """Request handler that processes POST requests with JSON payloads."""

    def do_POST(self):
        """Handle POST requests: read JSON, extract 'path', put into queue."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No content received")
            return

        try:
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            print(f"{payload=}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON payload")
            return

        path_value = payload.get("path", "")
        if not isinstance(path_value, str):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"'path' must be a string")
            return

        sync_queue.put(path_value)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Path written to queue")

    def log_message(self, format, *args):
        """Override to suppress default logging to stderr."""
        return


def _download_worker():
    last_download_time = 0
    while True:
        time_since_last_download = (
            int(time.monotonic()) - last_download_time if last_download_time > 0 else 0
        )
        try:
            path = sync_queue.get_nowait()
            download_filename = path.replace(SRC_DIR, "")
            dst_filename = f"{DEST_DIR}{download_filename}"
            full_url = f"{BASE_URL}{download_filename}"
            urllib.request.urlretrieve(full_url, dst_filename)
            print(f"Synced {full_url} to {dst_filename}")

            sync_queue.task_done()
            last_download_time = int(time.monotonic())
        except queue.Empty:
            if time_since_last_download > 1:
                last_download_time = 0
                test_runner()
        except Exception as e:
            print(f"Failed to download {path}: {e}")


def test_runner():
    """Run the gardenlinux tests and print stdout and stderr."""
    print("Calling test runner")
    # cmd = [TESTS_RUNNER]  # TODO: add cmdline args here
    # try:
    #     result = subprocess.run(
    #         cmd,
    #         capture_output=True,
    #         text=True,
    #         check=False,
    #     )
    #     if result.stdout:
    #         print(result.stdout, end="")
    #     if result.stderr:
    #         print(result.stderr, end="")
    # except Exception as e:
    #     print(f"Error running test_runner: {e}")


def run_server(host="0.0.0.0", port=9999):
    with socketserver.TCPServer((host, port), NotifyHandler) as httpd:
        print(f"Serving on {host}:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    worker_thread = threading.Thread(target=_download_worker, daemon=True)
    worker_thread.start()

    run_server()
