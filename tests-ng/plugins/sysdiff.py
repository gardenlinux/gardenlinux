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
import gzip
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from debian import deb822

from .dpkg import Dpkg
from .kernel_module import KernelModule, LoadedKernelModule
from .shell import ShellRunner
from .sysctl import Sysctl, SysctlParam
from .systemd import Systemd, SystemdUnit

STATE_DIR = "/tmp/sysdiff"

DEFAULT_PATHS = [
    "/etc", "/boot", "/usr/local/bin", "/usr/local/sbin",
    "/usr/local/lib", "/opt", "/proc/mounts"
]

IGNORED_SYSTEMD_PATTERNS = [
    # sysstat services run periodically
    'sysstat-collect.service',
    'sysstat-collect.timer',
    'sysstat-rotate.timer',
    'sysstat-summary.timer',
]
IGNORED_KERNEL_MODULES = []
IGNORED_SYSCTL_PARAMS = {
    # File system dynamic parameters
    'fs.dentry-state',
    'fs.file-nr',
    'fs.inode-nr',
    'fs.inode-state',
    'fs.quota.allocated_dquots',
    'fs.quota.cache_hits',
    'fs.quota.drops',
    'fs.quota.free_dquots',
    'fs.quota.lookups',
    'fs.quota.reads',
    'fs.quota.syncs',
    'fs.quota.writes',

    # Kernel dynamic parameters
    'kernel.ns_last_pid',
    'kernel.random.uuid',

    # Network dynamic parameters
    'net.netfilter.nf_conntrack_count',

    # Memory dynamic parameters
    'vm.nr_pdflush_threads',
    'vm.stat.nr_dirty',
    'vm.stat.nr_writeback',
    'vm.stat.nr_unstable',
    'vm.stat.nr_page_table_pages',
    'vm.stat.nr_mapped',
    'vm.stat.nr_slab',
    'vm.stat.nr_pagecache',
    'vm.stat.nr_reverse_maps',
    'vm.stat.nr_dirty_background_threshold',
    'vm.stat.nr_dirty_threshold',
    'vm.stat.nr_dirty_background',
    'vm.stat.nr_dirty',
    'vm.stat.nr_writeback',
    'vm.stat.nr_unstable',
    'vm.stat.nr_page_table_pages',
    'vm.stat.nr_mapped',
    'vm.stat.nr_slab',
    'vm.stat.nr_pagecache',
    'vm.stat.nr_reverse_maps',
}


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
    packages: List[deb822.Deb822]
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
        except Exception as e:
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

    def __init__(self, state_dir: Path | None = None):
        self.state_dir = state_dir or Path(STATE_DIR)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, name: str | None = None, paths: List[str] | None = None,
                       ignore_file: Path | None = None, verbose: bool = False) -> Snapshot:
        """Create a new system snapshot"""
        if paths is None:
            paths = DEFAULT_PATHS

        now = datetime.now()
        timestamp = now.isoformat()

        try:
            user = os.getlogin()
        except OSError:
            # Fallback when there's no controlling terminal (e.g., Github Actions)
            user = os.environ.get('USER')

        if name is None:
            snapshot_name = timestamp
        else:
            snapshot_name = f"{timestamp}-{user}-{name}"

        snapshot_file = self.state_dir / f"{snapshot_name}.json.gz"
        if snapshot_file.exists():
            raise ValueError(f"Snapshot '{snapshot_name}' already exists at {snapshot_file}")

        shell = ShellRunner(None)
        dpkg = Dpkg(shell)
        systemd = Systemd(shell)
        file_collector = FileCollector(shell)
        sysctl_collector = Sysctl(shell)
        kernel_module = KernelModule(shell)

        packages = dpkg.collect_installed_packages().packages

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

        snapshot = Snapshot(snapshot_name, metadata, packages, systemd_units, files, sysctl_params, kernel_modules)
        self._save_snapshot(snapshot, snapshot_file)

        return snapshot

    def _save_snapshot(self, snapshot: Snapshot, snapshot_file: Path):
        """Save snapshot to disk as compressed JSON"""
        self.state_dir.mkdir(parents=True, exist_ok=True)

        snapshot_data = {
            "name": snapshot.name,
            "metadata": asdict(snapshot.metadata),
            "packages": [dict(pkg) for pkg in snapshot.packages],
            "systemd_units": [asdict(unit) for unit in snapshot.systemd_units],
            "files": [asdict(file_entry) for file_entry in snapshot.files],
            "sysctl_params": [asdict(param) for param in snapshot.sysctl_params],
            "kernel_modules": [asdict(module) for module in snapshot.kernel_modules]
        }

        with gzip.open(snapshot_file, 'wt', encoding='utf-8') as f:
            json.dump(snapshot_data, f, separators=(',', ':'), sort_keys=True)

    def load_snapshot(self, name: str) -> Snapshot:
        """Load snapshot from disk"""
        snapshot_file = self.state_dir / f"{name}.json.gz"
        if not snapshot_file.exists():
            raise ValueError(f"Snapshot '{name}' not found")

        with gzip.open(snapshot_file, 'rt', encoding='utf-8') as f:
            snapshot_data = json.load(f)

        metadata = SnapshotMetadata(**snapshot_data["metadata"])
        packages = [deb822.Deb822(pkg_data) for pkg_data in snapshot_data["packages"]]
        systemd_units = [SystemdUnit(**unit_data) for unit_data in snapshot_data["systemd_units"]]
        files = [FileEntry(**file_data) for file_data in snapshot_data["files"]]
        sysctl_params = [SysctlParam(**param_data) for param_data in snapshot_data["sysctl_params"]]
        kernel_modules = [LoadedKernelModule(**module_data) for module_data in snapshot_data["kernel_modules"]]

        return Snapshot(name, metadata, packages, systemd_units, files, sysctl_params, kernel_modules)

    def list_snapshots(self) -> List[str]:
        """List all available snapshots"""
        if not self.state_dir.exists():
            return []

        snapshots = []
        for item in self.state_dir.iterdir():
            if item.is_file() and item.name.endswith('.json.gz'):
                snapshot_name = item.name[:-8]  # Remove '.json.gz'
                snapshots.append(snapshot_name)

        return sorted(snapshots)


class DiffEngine:
    """Handles comparison between snapshots"""

    def __init__(self):
        self._ignored_systemd_units = set(IGNORED_SYSTEMD_PATTERNS)
        self._ignored_kernel_modules = set(IGNORED_KERNEL_MODULES)
        self._ignored_sysctl_params = set(IGNORED_SYSCTL_PARAMS)

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

    def _compare_packages(self, packages_a: List[deb822.Deb822], packages_b: List[deb822.Deb822]) -> List[str]:
        """Compare package lists and return diff lines"""
        lines_a = [f"{pkg.get('Package', '')}\t{pkg.get('Version', '')}" for pkg in packages_a]
        lines_b = [f"{pkg.get('Package', '')}\t{pkg.get('Version', '')}" for pkg in packages_b]

        return self._generate_diff(
            lines_a, lines_b,
            "packages@snapshot_a", "packages@snapshot_b"
        )

    def _compare_systemd_units(self, units_a: List[SystemdUnit], units_b: List[SystemdUnit]) -> List[str]:
        """Compare systemd unit lists and return diff lines"""
        def format_unit(unit: SystemdUnit) -> str:
            """Format unit for comparison"""
            return f"{unit.unit}\t{unit.load}\t{unit.active}\t{unit.sub}"

        filtered_units_a = [format_unit(u) for u in units_a if u.unit not in self._ignored_systemd_units]
        filtered_units_b = [format_unit(u) for u in units_b if u.unit not in self._ignored_systemd_units]

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
        filtered_params_a = [param for param in params_a if param.name not in self._ignored_sysctl_params]
        filtered_params_b = [param for param in params_b if param.name not in self._ignored_sysctl_params]

        lines_a = [str(param) for param in filtered_params_a]
        lines_b = [str(param) for param in filtered_params_b]

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

    def create_snapshot(self, name: str | None = None, paths: List[str] | None = None,
                       ignore_file: Path | None = None, verbose: bool = False) -> Snapshot:
        """Create a snapshot using the shell context"""
        return self.manager.create_snapshot(name, paths, ignore_file, verbose)

    def load_snapshot(self, name: str) -> Snapshot:
        """Load a snapshot"""
        return self.manager.load_snapshot(name)

    def compare_snapshots(self, name_a: str, name_b: str) -> DiffResult:
        """Compare two snapshots"""
        snapshot_a = self.manager.load_snapshot(name_a)
        snapshot_b = self.manager.load_snapshot(name_b)
        return self.diff_engine.compare_snapshots(snapshot_a, snapshot_b)

    def cleanup_snapshots(self, names: List[str]):
        """Cleanup snapshots"""
        for name in names:
            snapshot_file = self.manager.state_dir / f"{name}.json.gz"
            if snapshot_file.exists():
                snapshot_file.unlink()
        # if the state_dir is empty, delete it
        if not os.listdir(self.manager.state_dir):
            shutil.rmtree(self.manager.state_dir)



@pytest.fixture
def sysdiff(shell: ShellRunner):
    """Function-scoped sysdiff fixture for individual tests."""
    return Sysdiff(shell)
