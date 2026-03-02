import grp
import os
import pwd
import stat
from pathlib import Path
from typing import Tuple

import pytest


class File:
    """Pytest-facing facade for file metadata operations.

    Provides path-based helpers for checking file metadata such as
    existence, type, permissions, ownership, etc.
    """

    def exists(self, path: str | Path) -> bool:
        """Check if a path exists (any type).

        Args:
            path: File path.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return Path(path).exists()

    def is_regular_file(self, path: str | Path) -> bool:
        """Check if a path is a regular file.

        Does not follow symlinks - symlinks return False even if they point to files.

        Args:
            path: File path.

        Returns:
            bool: True if the path is a regular file, False otherwise.
        """
        p = Path(path)
        try:
            return stat.S_ISREG(p.lstat().st_mode)
        except (OSError, FileNotFoundError):
            return False

    def is_dir(self, path: str | Path) -> bool:
        """Check if a path is a directory.

        Does not follow symlinks - symlinks return False even if they point to directories.

        Args:
            path: File path.

        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        return Path(path).is_dir(follow_symlinks=False)

    def _resolve_path(self, base_path: Path, path_to_resolve: str | Path) -> Path:
        """Resolve a path relative to a base path's parent if relative, or absolutely if absolute.

        Args:
            base_path: Base path (typically the symlink itself).
            path_to_resolve: Path to resolve (can be relative or absolute).

        Returns:
            Path: Resolved absolute path.
        """
        path = Path(path_to_resolve)
        if path.is_absolute():
            return path.resolve()
        else:
            return (base_path.parent / path).resolve()

    def is_symlink(
        self,
        path: str | Path,
        target: str | Path | None = None,
        error_on_broken_symlink: bool = True,
    ) -> bool:
        """Check if a path is a symlink, optionally validating the target.

        Args:
            path: File path.
            target: Optional target path to validate. If provided, checks that the
                symlink points to this target. Can be a string or Path object.
                The comparison handles both relative and absolute paths.
            error_on_broken_symlink: If True (default), raise an error if the symlink
                is broken (target doesn't exist). If False, return True for any
                symlink regardless of whether the target exists.

        Returns:
            bool: True if the path is a symlink and (if target is provided) points
                to the specified target, False otherwise.

        Raises:
            FileNotFoundError: If error_on_broken_symlink is True and the symlink
                target does not exist.
        """
        p = Path(path)
        if not p.is_symlink():
            return False

        if target is None:
            if error_on_broken_symlink and not p.exists():
                raise FileNotFoundError(
                    f"Broken symlink: {path} -> target does not exist"
                )
            return True

        symlink_target = p.readlink()
        resolved_symlink_target = self._resolve_path(p, symlink_target)
        resolved_expected_target = self._resolve_path(p, target)

        if resolved_symlink_target != resolved_expected_target:
            return False

        if error_on_broken_symlink and not resolved_symlink_target.exists():
            raise FileNotFoundError(
                f"Broken symlink: {path} -> {symlink_target} (target does not exist)"
            )

        return True

    def get_mode(self, path: str | Path) -> str:
        """Get file permissions as octal string.

        Args:
            path: File path.

        Returns:
            str: File permissions as octal string (e.g., "0755").

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        mode_int = stat.S_IMODE(Path(path).stat().st_mode)
        return f"{mode_int:04o}"

    def has_mode(self, path: str | Path, mode: str) -> bool:
        """Check if a file has specific permissions.

        Args:
            path: File path.
            mode: Expected permissions as octal string (e.g., "0755").

        Returns:
            bool: True if the file has the specified permissions, False otherwise.

        Raises:
            TypeError: If mode is not a string.
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        if not isinstance(mode, str):
            raise TypeError(
                f"mode must be a string (e.g., '0755'), got {type(mode).__name__}"
            )
        return self.get_mode(path) == mode

    def is_executable(self, path: str | Path) -> bool:
        """Check if a file is executable.

        Args:
            path: File path.

        Returns:
            bool: True if the file is executable, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        path_str = str(path) if isinstance(path, Path) else path
        # os.access() doesn't raise FileNotFoundError, so check existence first
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return os.access(path_str, os.X_OK)

    def is_readable(self, path: str | Path) -> bool:
        """Check if a file is readable.

        Args:
            path: File path.

        Returns:
            bool: True if the file is readable, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        path_str = str(path) if isinstance(path, Path) else path
        # os.access() doesn't raise FileNotFoundError, so check existence first
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return os.access(path_str, os.R_OK)

    def is_writable(self, path: str | Path) -> bool:
        """Check if a file is writable.

        Args:
            path: File path.

        Returns:
            bool: True if the file is writable, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        path_str = str(path) if isinstance(path, Path) else path
        # os.access() doesn't raise FileNotFoundError, so check existence first
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return os.access(path_str, os.W_OK)

    def get_size(self, path: str | Path) -> int:
        """Get file size in bytes.

        Args:
            path: File path.

        Returns:
            int: File size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return Path(path).stat().st_size

    def get_owner(self, path: str | Path) -> Tuple[str, str]:
        """Get file ownership (user, group).

        Args:
            path: File path.

        Returns:
            Tuple[str, str]: A tuple of (username, groupname).

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        user = self.get_user(path)
        group = self.get_group(path)
        return (user, group)

    def get_user(self, path: str | Path) -> str:
        """Get file owner username.

        Args:
            path: File path.

        Returns:
            str: Username of the file owner.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        stat_info = Path(path).stat()
        return pwd.getpwuid(stat_info.st_uid).pw_name

    def get_group(self, path: str | Path) -> str:
        """Get file owner group name.

        Args:
            path: File path.

        Returns:
            str: Group name of the file owner.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        stat_info = Path(path).stat()
        return grp.getgrgid(stat_info.st_gid).gr_name

    def is_owned_by_user(self, path: str | Path, user: str) -> bool:
        """Check if a file is owned by a specific user.

        Args:
            path: File path.
            user: Expected username.

        Returns:
            bool: True if the file is owned by the specified user, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return self.get_user(path) == user

    def is_owned_by_group(self, path: str | Path, group: str) -> bool:
        """Check if a file is owned by a specific group.

        Args:
            path: File path.
            group: Expected group name.

        Returns:
            bool: True if the file is owned by the specified group, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return self.get_group(path) == group

    def is_owned_by(self, path: str | Path, user: str, group: str) -> bool:
        """Check if a file is owned by a specific user and group.

        Args:
            path: File path.
            user: Expected username.
            group: Expected group name.

        Returns:
            bool: True if the file is owned by the specified user and group, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return self.get_user(path) == user and self.get_group(path) == group


@pytest.fixture
def file() -> File:
    """Fixture providing the ``File`` helper for file metadata operations."""
    return File()
