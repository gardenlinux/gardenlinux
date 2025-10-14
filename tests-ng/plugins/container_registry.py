import pathlib
import hashlib
import gzip
import tarfile
import json
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import pytest


class RegistryHandler(BaseHTTPRequestHandler):
    """Handles only the endpoints needed for a Docker/Containerd pull."""

    server_version = "MockOCIRegistry/1.0"

    def _handle_request(self, head: bool = False):
        parsed = urlparse(self.path)
        path_parts = [p for p in parsed.path.split('/') if p]  # strip empty parts
        if parsed.path == "/v2/":
            self._handle_v2_root(head=head)
        elif len(path_parts) == 4 and path_parts[0] == 'v2':
            if path_parts[2] == 'manifests':
                self._handle_get_manifest(path_parts[1], path_parts[3], head=head)
                return
            elif path_parts[2] == 'blobs':
                self._handle_get_blob(path_parts[1], path_parts[3], head=head)
                return
        self._send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_GET(self):
        self._handle_request(head=False)

    def do_HEAD(self):
        self._handle_request(head=True)

    def _handle_v2_root(self, head=False):
        """Responds to /v2/"""
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Docker-Distribution-API-Version", "registry/2.0")
        self.end_headers()
        if not head:
            self.wfile.write(b'{}')

    def _handle_get_manifest(self, repo: str, tag: str, head: bool = False):
        """Serve the manifest for any repo/tag."""
        # The manifest we built is the same for any repo/tag
        data, size = self.server.builder.get_manifest()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type",
                         "application/vnd.docker.distribution.manifest.v2+json")
        self.send_header("Content-Length", str(size))
        self.send_header("Docker-Content-Digest", self.server.builder.manifest_digest)
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def _handle_get_blob(self, repo: str, digest: str, head=False):
        """Serve a blob – config or a layer."""
        # The digest is expected to be in the form sha256:<hash>
        if not digest.startswith("sha256:"):
            self._send_error(HTTPStatus.BAD_REQUEST, "Invalid digest")
            return
        blob = self.server.builder.get_blob(digest)
        if blob is None:
            self._send_error(HTTPStatus.NOT_FOUND, "Blob not found")
            return

        data, size = blob
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(size))
        self.send_header("Docker-Content-Digest", digest)
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))


class ContainerRegistry:
    """
    Self-contained pull-only container registry that serves a single image for all requests.
    Image to be supplied as a tarball (can be created using "docker save" command).
    """

    def __init__(self, tarball_filepath):
        self.blobs = {}          # digest -> (bytes, size)
        self.manifest_bytes = None
        self.manifest_digest = None
        self.repo_name = "mockrepo"
        self.tag = "latest"

        self.create_http_server()
        self.server_thread = None

        with tarfile.open(tarball_filepath, mode="r") as tar:
            try:
                manifest_member = tar.getmember("manifest.json")
            except KeyError:
                raise FileNotFoundError("tarball missing manifest.json")
            manifest_bytes = tar.extractfile(manifest_member).read()
            manifest_json = json.loads(manifest_bytes)

            if not isinstance(manifest_json, list) or not manifest_json:
                raise ValueError("manifest.json is not a non‑empty list")

            image_desc = manifest_json[0]
            config_file = image_desc["Config"]
            layer_files = image_desc["Layers"]

            config_member = tar.getmember(config_file)
            config_bytes = tar.extractfile(config_member).read()
            config_digest = self.sha256_digest(config_bytes)
            self.blobs[config_digest] = (config_bytes, len(config_bytes))

            layer_entries = []
            for idx, layer_file in enumerate(layer_files):
                layer_member = tar.getmember(layer_file)
                layer_bytes = tar.extractfile(layer_member).read()
                gz_layer = self.gzip_bytes(layer_bytes)
                layer_digest = self.sha256_digest(gz_layer)
                self.blobs[layer_digest] = (gz_layer, len(gz_layer))
                layer_entries.append({
                    "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                    "size": len(gz_layer),
                    "digest": layer_digest,
                })

            self.manifest_bytes = json.dumps({
                "schemaVersion": 2,
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "config": {
                    "mediaType": "application/vnd.docker.container.image.v1+json",
                    "size": len(config_bytes),
                    "digest": config_digest,
                },
                "layers": layer_entries,
            }).encode("utf-8")
            self.manifest_digest = self.sha256_digest(self.manifest_bytes)
            self.blobs[self.manifest_digest] = (self.manifest_bytes, len(self.manifest_bytes))

    def create_http_server(self):
        self.server = HTTPServer(("127.0.0.1", 5000), RegistryHandler)
        self.server.builder = self

    def start(self):
        def serve(server):
            server.serve_forever()

        self.server_thread = threading.Thread(target=serve, args=[self.server], daemon=True)
        self.server_thread.start()
        time.sleep(0.2)

    def shutdown(self):
        self.server.shutdown()
        self.server_thread.join(timeout=2)
        self.server.server_close()

    def sha256_digest(self, data: bytes) -> str:
        """Return a Docker‑style SHA256 digest string."""
        return f"sha256:{hashlib.sha256(data).hexdigest()}"

    def gzip_bytes(self, data: bytes) -> bytes:
        """Return gzipped bytes (gzip format)."""
        return gzip.compress(data)

    def get_blob(self, digest: str):
        """Return (bytes, size) for a digest, or None if missing."""
        return self.blobs.get(digest)

    def get_manifest(self):
        """Return the manifest bytes and its size."""
        return self.manifest_bytes, len(self.manifest_bytes)


@pytest.fixture
def container_registry():
    this_file = pathlib.Path(__file__).resolve()
    plugin_dir = this_file.parent
    container_image_tarball = plugin_dir / "busybox.tar"
    return ContainerRegistry(container_image_tarball)
