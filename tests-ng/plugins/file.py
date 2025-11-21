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

    def is_file(self, path: str | Path) -> bool:
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
        p = Path(path)
        try:
            return stat.S_ISDIR(p.lstat().st_mode)
        except (OSError, FileNotFoundError):
            return False

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

        if target is not None:
            symlink_target = p.readlink()
            target_path = Path(target)

            # Normalize both paths for comparison
            symlink_parent = p.parent.resolve()

            # Resolve the symlink's actual target
            if symlink_target.is_absolute():
                resolved_symlink_target = symlink_target.resolve()
            else:
                resolved_symlink_target = (symlink_parent / symlink_target).resolve()

            # Resolve the expected target path
            if target_path.is_absolute():
                resolved_target = target_path.resolve()
            else:
                resolved_target = (symlink_parent / target_path).resolve()

            if resolved_symlink_target != resolved_target:
                return False

            if error_on_broken_symlink and not resolved_symlink_target.exists():
                raise FileNotFoundError(
                    f"Broken symlink: {path} -> {symlink_target} (target does not exist)"
                )

            return True

        if error_on_broken_symlink and not p.exists():
            raise FileNotFoundError(f"Broken symlink: {path} -> target does not exist")

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

    def _check_permission(self, path: str | Path, permission_type: str) -> bool:
        """Check file permission using stat.

        Args:
            path: File path.
            permission_type: 'read', 'write', or 'execute'.

        Returns:
            bool: True if the current user has the specified permission, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        stat_info = Path(
            path
        ).stat()  # Raises FileNotFoundError or PermissionError naturally
        mode = stat_info.st_mode
        current_uid = os.getuid()
        current_gids = {os.getgid()} | set(os.getgroups())

        # Map permission types to (owner, group, other) bit masks
        permission_bits = {
            "read": (stat.S_IRUSR, stat.S_IRGRP, stat.S_IROTH),
            "write": (stat.S_IWUSR, stat.S_IWGRP, stat.S_IWOTH),
            "execute": (stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH),
        }
        if permission_type not in permission_bits:
            raise ValueError(f"Invalid permission_type: {permission_type}")

        owner_bit, group_bit, other_bit = permission_bits[permission_type]

        # Determine which bit to check based on ownership
        if stat_info.st_uid == current_uid:
            bit_to_check = owner_bit
        elif stat_info.st_gid in current_gids:
            bit_to_check = group_bit
        else:
            bit_to_check = other_bit

        return bool(mode & bit_to_check)

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
        return self._check_permission(path, "execute")

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
        return self._check_permission(path, "read")

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
        return self._check_permission(path, "write")

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
        stat_info = Path(path).stat()
        user = pwd.getpwuid(stat_info.st_uid).pw_name
        group = grp.getgrgid(stat_info.st_gid).gr_name
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

    def has_user(self, path: str | Path, user: str) -> bool:
        """Check if a file has a specific owner user.

        Args:
            path: File path.
            user: Expected username.

        Returns:
            bool: True if the file has the specified user, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return self.get_user(path) == user

    def has_group(self, path: str | Path, group: str) -> bool:
        """Check if a file has a specific owner group.

        Args:
            path: File path.
            group: Expected group name.

        Returns:
            bool: True if the file has the specified group, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return self.get_group(path) == group

    def has_owner(self, path: str | Path, user: str, group: str) -> bool:
        """Check if a file has a specific owner (user and group).

        Args:
            path: File path.
            user: Expected username.
            group: Expected group name.

        Returns:
            bool: True if the file has the specified user and group, False otherwise.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If permission to access the path is denied.
        """
        return self.get_user(path) == user and self.get_group(path) == group


@pytest.fixture
def file() -> File:
    """Fixture providing the ``File`` helper for file metadata operations."""
    return File()
