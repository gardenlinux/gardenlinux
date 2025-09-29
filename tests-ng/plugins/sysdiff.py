"""
System state snapshot and diff functionality for tests-ng.

Provides snapshot and comparison capabilities for:
- packages (dpkg)
- systemd units
- files (sha256 checksums)
- sysctl parameters
- loaded kernel modules
"""

import difflib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

from .shell import ShellRunner
from .dpkg import Dpkg, Package
from .systemd import Systemd, SystemdUnit
from .kernel_module import KernelModule, LoadedKernelModule
from .sysctl import Sysctl, SysctlParam


DEFAULT_PATHS = [
    "/etc", "/boot", "/usr/local/bin", "/usr/local/sbin",
    "/usr/local/lib", "/opt", "/proc/mounts"
]

STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "sysdiff"

IGNORED_SYSTEMD_PATTERNS = []
IGNORED_KERNEL_MODULES = []


@dataclass
class FileEntry:
    """Represents a file with its hash"""
    path: str
    sha256: str

    def __str__(self) -> str:
        return f"{self.sha256}  {self.path}"


@dataclass
class SnapshotMetadata:
    """Metadata for a snapshot"""
    created_at: str
    paths: List[str]
    ignore_file: bool


@dataclass
class Snapshot:
    """Complete system snapshot"""
    name: str
    metadata: SnapshotMetadata
    packages: List[Package]
    systemd_units: List[SystemdUnit]
    files: List[FileEntry]
    sysctl_params: List[SysctlParam]
    kernel_modules: List[LoadedKernelModule]  # loaded kernel modules


@dataclass
class DiffResult:
    """Result of comparing two snapshots"""
    package_changes: List[str]
    systemd_changes: List[str]
    file_changes: List[str]
    sysctl_changes: List[str]
    kernel_module_changes: List[str]
    has_changes: bool


class FileCollector:
    """Collects file hashes and handles filtering"""

    def __init__(self, shell: ShellRunner):
        self.shell = shell

    def normalize_paths(self, paths: List[str]) -> List[str]:
        """Deduplicate and keep only existing directories/files"""
        existing_paths = []
        seen = set()

        for path in paths:
            if path and path not in seen:
                try:
                    if os.path.exists(path):
                        existing_paths.append(path)
                        seen.add(path)
                except Exception as e:
                    print(f"Error normalizing paths: {e}")

        return existing_paths

    def load_ignore_patterns(self, ignore_file: Optional[Path]) -> List[str]:
        """Load ignore patterns from file"""
        if not ignore_file or not ignore_file.exists():
            return []

        patterns = []
        try:
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception:
            print(f"Error loading ignore patterns from {ignore_file}: {e}")

        return patterns

    def should_ignore_file(self, filepath: str, ignore_patterns: List[str]) -> bool:
        """Check if file should be ignored based on patterns"""
        for pattern in ignore_patterns:
            try:
                if re.search(pattern, filepath):
                    return True
            except re.error:
                # If pattern is invalid regex, treat as literal string
                if pattern in filepath:
                    return True
        return False

    def _walk_files_recursive(self, root: str):
        """Yield all files under root, recursively, without crossing filesystem boundaries."""
        if os.path.isfile(root):
            yield root
            return

        if not os.path.isdir(root):
            return

        try:
            root_dev = os.stat(root).st_dev
        except (OSError, IOError) as e:
            print(f"Warning: Cannot access {root}: {e}")
            return

        for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
            # Prevent crossing filesystem boundaries
            try:
                dir_dev = os.stat(dirpath).st_dev
                if dir_dev != root_dev:
                    dirnames[:] = []  # Don't descend into subdirectories
                    continue
            except (OSError, IOError):
                dirnames[:] = []  # Skip inaccessible directories
                continue

            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                yield filepath

    def _calculate_file_hash(self, filepath: str, verbose: bool = False) -> Optional[str]:
        """Calculate SHA256 hash for a single file"""
        import hashlib

        # Check if file exists before trying to read it
        try:
            if not os.path.exists(filepath):
                if verbose:
                    print(f"Warning: File not found: {filepath}")
                return None
        except (OSError, IOError):
            # If we can't even check existence, skip silently
            return None

        try:
            with open(filepath, "rb") as fileobj:
                sha256 = hashlib.sha256()
                # Read file in chunks for memory efficiency
                while True:
                    chunk = fileobj.read(8192)
                    if not chunk:
                        break
                    sha256.update(chunk)
                return sha256.hexdigest()
        except FileNotFoundError:
            # This shouldn't happen after the exists check, but handle it gracefully
            if verbose:
                print(f"Warning: File disappeared: {filepath}")
            return None
        except (OSError, IOError, PermissionError) as e:
            # Less common errors - always warn
            print(f"Warning: Cannot read {filepath}: {e}")
            return None

    def collect_file_hashes(self, paths: List[str], ignore_patterns: Optional[List[str]] = None,
                          verbose: bool = False) -> Dict[str, str]:
        """
        Collect SHA256 hashes for files in given paths, recursively.

        Args:
            paths: List of file/directory paths to scan
            ignore_patterns: List of regex patterns for files to ignore
            verbose: If True, show warnings for missing files (broken symlinks)

        Returns:
            Dictionary mapping file paths to their SHA256 hashes
        """
        import hashlib

        if ignore_patterns is None:
            ignore_patterns = []

        file_hashes: Dict[str, str] = {}

        if not paths:
            return file_hashes

        try:
            all_files = []
            for path in paths:
                try:
                    files_in_path = list(self._walk_files_recursive(path))
                    all_files.extend(files_in_path)
                except Exception as e:
                    print(f"Warning: Error scanning {path}: {e}")
                    continue

            filtered_files = [
                f for f in all_files
                if not self.should_ignore_file(f, ignore_patterns)
            ]

            filtered_files.sort()

            for filepath in filtered_files:
                hash_value = self._calculate_file_hash(filepath, verbose)
                if hash_value is not None:
                    file_hashes[filepath] = hash_value

        except Exception as e:
            print(f"Error collecting file hashes: {e}")

        return file_hashes


class SnapshotManager:
    """Manages snapshot creation, storage, and retrieval"""

    def __init__(self, state_dir: Path = None):
        self.state_dir = state_dir or STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, name: str = None, paths: List[str] = None,
                       ignore_file: Path = None, verbose: bool = False) -> Snapshot:
        """Create a new system snapshot"""
        if paths is None:
            paths = DEFAULT_PATHS

        if name is None:
            name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        snapdir = self.state_dir / name
        if snapdir.exists():
            raise ValueError(f"Snapshot '{name}' already exists at {snapdir}")

        snapdir.mkdir(parents=True)

        shell = ShellRunner(None)
        dpkg = Dpkg(shell)
        systemd = Systemd(shell)
        file_collector = FileCollector(shell)
        sysctl_collector = Sysctl(shell)
        kernel_module = KernelModule(shell)

        packages_dict = dpkg.collect_packages()
        packages = [Package(name=pkg, version=ver) for pkg, ver in packages_dict.items()]

        systemd_units = systemd.list_units()

        sysctl_params_dict = sysctl_collector.collect_sysctl_parameters()
        sysctl_params = [SysctlParam(name=param, value=val) for param, val in sysctl_params_dict.items()]

        kernel_modules_list = kernel_module.collect_loaded_modules()
        kernel_modules = [LoadedKernelModule(name=module) for module in kernel_modules_list]

        ignore_patterns = file_collector.load_ignore_patterns(ignore_file)
        normalized_paths = file_collector.normalize_paths(paths)

        files_dict = file_collector.collect_file_hashes(normalized_paths, ignore_patterns, verbose)
        files = [FileEntry(path=path, sha256=hash_val) for path, hash_val in files_dict.items()]

        metadata = SnapshotMetadata(
            created_at=datetime.now().isoformat(),
            paths=normalized_paths,
            ignore_file=bool(ignore_file and ignore_file.exists())
        )

        snapshot = Snapshot(name, metadata, packages, systemd_units, files, sysctl_params, kernel_modules)
        self._save_snapshot(snapshot, snapdir)

        return snapshot

    def _save_snapshot(self, snapshot: Snapshot, snapdir: Path):
        """Save snapshot to disk"""

        with open(snapdir / "packages.txt", 'w') as f:
            for package in snapshot.packages:
                f.write(f"{package.name}\t{package.version}\n")

        with open(snapdir / "systemd_units.txt", 'w') as f:
            for unit in snapshot.systemd_units:
                f.write(f"{unit.unit}\t{unit.load}\t{unit.active}\t{unit.sub}\n")

        with open(snapdir / "files.txt", 'w') as f:
            for file_entry in sorted(snapshot.files, key=lambda f: f.path):
                f.write(f"{file_entry.sha256}  {file_entry.path}\n")

        with open(snapdir / "sysctl.txt", 'w') as f:
            for param in snapshot.sysctl_params:
                f.write(f"{param.name}={param.value}\n")

        with open(snapdir / "kernel_modules.txt", 'w') as f:
            for module in snapshot.kernel_modules:
                f.write(f"{module.name}\n")

        with open(snapdir / "meta", 'w') as f:
            f.write(f"created_at={snapshot.metadata.created_at}\n")
            f.write(f"paths={' '.join(snapshot.metadata.paths)}\n")
            f.write(f"ignore_file={'present' if snapshot.metadata.ignore_file else ''}\n")

    def load_snapshot(self, name: str) -> Snapshot:
        """Load snapshot from disk"""
        snapdir = self.state_dir / name
        if not snapdir.exists():
            raise ValueError(f"Snapshot '{name}' not found")

        packages = []
        packages_file = snapdir / "packages.txt"
        if packages_file.exists():
            with open(packages_file, 'r') as f:
                for line in f:
                    if '\t' in line:
                        package, version = line.strip().split('\t', 1)
                        packages.append(Package(name=package, version=version))

        systemd_units = []
        systemd_file = snapdir / "systemd_units.txt"
        if systemd_file.exists():
            with open(systemd_file, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 4:
                        systemd_units.append(SystemdUnit(
                            unit=parts[0],
                            load=parts[1],
                            active=parts[2],
                            sub=parts[3]
                        ))

        files = []
        files_file = snapdir / "files.txt"
        if files_file.exists():
            with open(files_file, 'r') as f:
                for line in f:
                    parts = line.strip().split('  ', 1)
                    if len(parts) == 2:
                        files.append(FileEntry(path=parts[1], sha256=parts[0]))

        sysctl_params = []
        sysctl_file = snapdir / "sysctl.txt"
        if sysctl_file.exists():
            with open(sysctl_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        param, value = line.strip().split('=', 1)
                        sysctl_params.append(SysctlParam(name=param, value=value))

        kernel_modules = []
        kernel_modules_file = snapdir / "kernel_modules.txt"
        if kernel_modules_file.exists():
            with open(kernel_modules_file, 'r') as f:
                for line in f:
                    module = line.strip()
                    if module:
                        kernel_modules.append(LoadedKernelModule(name=module))

        metadata = SnapshotMetadata(
            created_at="",
            paths=[],
            ignore_file=False,
        )
        meta_file = snapdir / "meta"
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == "created_at":
                            metadata.created_at = value
                        elif key == "paths":
                            metadata.paths = value.split() if value else []
                        elif key == "ignore_file":
                            metadata.ignore_file = value == "present"

        return Snapshot(name, metadata, packages, systemd_units, files, sysctl_params, kernel_modules)

    def list_snapshots(self) -> List[str]:
        """List all available snapshots"""
        if not self.state_dir.exists():
            return []

        snapshots = []
        for item in self.state_dir.iterdir():
            if item.is_dir():
                snapshots.append(item.name)

        return sorted(snapshots)


class DiffEngine:
    """Handles comparison between snapshots"""

    def __init__(self):
        self._compiled_patterns = [re.compile(pattern) for pattern in IGNORED_SYSTEMD_PATTERNS]
        self._ignored_kernel_modules = set(IGNORED_KERNEL_MODULES)

    def compare_snapshots(self, snapshot_a: Snapshot, snapshot_b: Snapshot) -> DiffResult:
        """Compare two snapshots and return differences"""
        changes = [
            self._compare_packages(snapshot_a.packages, snapshot_b.packages),
            self._compare_systemd_units(snapshot_a.systemd_units, snapshot_b.systemd_units),
            self._compare_files(snapshot_a.files, snapshot_b.files),
            self._compare_sysctl_params(snapshot_a.sysctl_params, snapshot_b.sysctl_params),
            self._compare_kernel_modules(snapshot_a.kernel_modules, snapshot_b.kernel_modules),
        ]

        return DiffResult(*changes, has_changes=any(changes))

    def _generate_diff(self, lines_a: List[str], lines_b: List[str],
                              fromfile: str, tofile: str) -> List[str]:
        """Generate diff for two line lists"""
        return list(difflib.unified_diff(
            lines_a, lines_b,
            fromfile=fromfile,
            tofile=tofile,
            lineterm=""
        ))

    def _compare_packages(self, packages_a: List[Package], packages_b: List[Package]) -> List[str]:
        """Compare package lists and return diff lines"""
        lines_a = [str(pkg) for pkg in packages_a]
        lines_b = [str(pkg) for pkg in packages_b]

        return self._generate_diff(
            lines_a, lines_b,
            "packages@snapshot_a", "packages@snapshot_b"
        )

    def _compare_systemd_units(self, units_a: List[SystemdUnit], units_b: List[SystemdUnit]) -> List[str]:
        """Compare systemd unit lists and return diff lines"""
        def should_ignore_unit(unit: SystemdUnit) -> bool:
            """Check if unit should be ignored based on filtering patterns"""
            return any(pattern.search(unit.unit) for pattern in self._compiled_patterns)

        def format_unit(unit: SystemdUnit) -> str:
            """Format unit for comparison"""
            return f"{unit.unit}\t{unit.load}\t{unit.active}\t{unit.sub}"

        filtered_units_a = [format_unit(u) for u in units_a if not should_ignore_unit(u)]
        filtered_units_b = [format_unit(u) for u in units_b if not should_ignore_unit(u)]

        return self._generate_diff(
            filtered_units_a, filtered_units_b,
            "systemd_units@snapshot_a", "systemd_units@snapshot_b"
        )

    def _compare_files(self, files_a: List[FileEntry], files_b: List[FileEntry]) -> List[str]:
        """Compare file lists and return diff lines"""
        lines_a = [str(file_entry) for file_entry in sorted(files_a, key=lambda f: f.path)]
        lines_b = [str(file_entry) for file_entry in sorted(files_b, key=lambda f: f.path)]

        return self._generate_diff(
            lines_a, lines_b,
            "files@snapshot_a", "files@snapshot_b"
        )

    def _compare_sysctl_params(self, params_a: List[SysctlParam], params_b: List[SysctlParam]) -> List[str]:
        """Compare sysctl parameter lists and return diff lines"""
        lines_a = [str(param) for param in params_a]
        lines_b = [str(param) for param in params_b]

        return self._generate_diff(
            lines_a, lines_b,
            "sysctl@snapshot_a", "sysctl@snapshot_b"
        )

    def _compare_kernel_modules(self, modules_a: List[LoadedKernelModule], modules_b: List[LoadedKernelModule]) -> List[str]:
        """Compare kernel module lists and return diff lines"""
        filtered_modules_a = [m for m in modules_a if m.name not in self._ignored_kernel_modules]
        filtered_modules_b = [m for m in modules_b if m.name not in self._ignored_kernel_modules]

        lines_a = sorted([str(module) for module in filtered_modules_a])
        lines_b = sorted([str(module) for module in filtered_modules_b])

        return self._generate_diff(
            lines_a, lines_b,
            "kernel_modules@snapshot_a", "kernel_modules@snapshot_b"
        )

    def generate_diff(self, diff_result: DiffResult, snapshot_a_name: str, snapshot_b_name: str) -> str:
        """Generate diff output compatible with shell script"""
        change_types = [
            ("Package changes", diff_result.package_changes),
            ("Systemd unit state changes", diff_result.systemd_changes),
            ("File content changes (sha256, path)", diff_result.file_changes),
            ("Sysctl parameter changes", diff_result.sysctl_changes),
            ("Kernel module changes", diff_result.kernel_module_changes),
        ]

        output = []
        for change_type, changes in change_types:
            if changes:
                output.append(f"=== {change_type} ({snapshot_a_name} -> {snapshot_b_name}) ===")
                output.extend(changes)
                output.append("")

        if diff_result.has_changes:
            output.append("Tip: lines starting with '+' mean new/changed; '-' mean removed/previous state.")

        return "\n".join(output)


class Sysdiff:
    """Main sysdiff class for tests-ng integration"""

    def __init__(self, shell: ShellRunner):
        self.shell = shell
        self.manager = SnapshotManager()
        self.diff_engine = DiffEngine()

    def create_snapshot(self, name: str, paths: List[str] = None,
                       ignore_file: Path = None, verbose: bool = False) -> Snapshot:
        """Create a snapshot using the shell context"""
        return self.manager.create_snapshot(name, paths, ignore_file, verbose)

    def compare_snapshots(self, name_a: str, name_b: str) -> DiffResult:
        """Compare two snapshots"""
        snapshot_a = self.manager.load_snapshot(name_a)
        snapshot_b = self.manager.load_snapshot(name_b)
        return self.diff_engine.compare_snapshots(snapshot_a, snapshot_b)

    def cleanup_snapshots(self, names: List[str]):
        """Cleanup snapshots"""
        for name in names:
            snapdir = self.manager.state_dir / name
            if snapdir.exists():
                import shutil
                shutil.rmtree(snapdir)


@pytest.fixture
def sysdiff(shell: ShellRunner):
    """Function-scoped sysdiff fixture for individual tests."""
    return Sysdiff(shell)
