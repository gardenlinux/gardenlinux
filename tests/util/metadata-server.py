#!/usr/bin/env python3
import http.server
import signal
import socketserver
import threading

API_VERSION = "2009-04-04"
BASE_PATH = f"/{API_VERSION}"
META_PATH = f"{BASE_PATH}/meta-data"
HOSTNAME = "gardenlinux"
INSTANCE_ID = "id-12345"
AMI_ID = "ami-12345"
AMI_INDEX = "0"
USER_DATA = f"#cloud-config\nhostname: {HOSTNAME}\n"
META_LIST = "instance-id\nlocal-hostname\nhostname\nami-id\nami-launch-index\n"


class MetadataHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        responses = {
            f"{META_PATH}/": META_LIST,
            f"{META_PATH}/instance-id": INSTANCE_ID,
            f"{META_PATH}/local-hostname": HOSTNAME,
            f"{META_PATH}/hostname": HOSTNAME,
            f"{META_PATH}/ami-id": AMI_ID,
            f"{META_PATH}/ami-launch-index": AMI_INDEX,
            f"{BASE_PATH}/user-data": USER_DATA,
        }

        if self.path in responses:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(responses[self.path].encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 8181), MetadataHandler)

    def shutdown_handler(signum, frame):
        """Handle shutdown signals by stopping the server in a separate thread."""
        threading.Thread(target=server.shutdown).start()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        server.serve_forever()
    finally:
        server.server_close()
