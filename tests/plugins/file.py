import grp
import os
import pwd
import stat
from pathlib import Path
from typing import Tuple

import pytest


class File:
    """Pytest-facing facade for file metadata operations."""

    # ------------------------------------------------------------------
    # Basic existence / type checks
    # ------------------------------------------------------------------

    def exists(self, path: str | Path) -> bool:
        return Path(path).exists()

    def is_regular_file(self, path: str | Path) -> bool:
        try:
            return stat.S_ISREG(Path(path).lstat().st_mode)
        except (OSError, FileNotFoundError):
            return False

    def is_dir(self, path: str | Path) -> bool:
        try:
            return stat.S_ISDIR(Path(path).lstat().st_mode)
        except (OSError, FileNotFoundError):
            return False

    # ------------------------------------------------------------------
    # Symlink handling
    # ------------------------------------------------------------------

    def _resolve_path(self, base: Path, target: str | Path) -> Path:
        target_path = Path(target)
        if target_path.is_absolute():
            return target_path.resolve()
        return (base.parent / target_path).resolve()

    def is_symlink(
        self,
        path: str | Path,
        target: str | Path | None = None,
        error_on_broken_symlink: bool = True,
    ) -> bool:
        p = Path(path)

        if not p.is_symlink():
            return False

        if target is None:
            if error_on_broken_symlink and not p.exists():
                raise FileNotFoundError(
                    f"Broken symlink: {path} -> target does not exist"
                )
            return True

        actual_target = self._resolve_path(p, p.readlink())
        expected_target = self._resolve_path(p, target)

        if actual_target != expected_target:
            return False

        if error_on_broken_symlink and not actual_target.exists():
            raise FileNotFoundError(
                f"Broken symlink: {path} -> {actual_target} (target does not exist)"
            )

        return True

    # ------------------------------------------------------------------
    # Permission handling
    # ------------------------------------------------------------------

    def get_mode(self, path: str | Path) -> str:
        mode_int = stat.S_IMODE(Path(path).stat().st_mode)
        return f"{mode_int:04o}"

    def has_mode(self, path: str | Path, mode: str) -> bool:
        if not isinstance(mode, str):
            raise TypeError(
                f"mode must be string (e.g., '0755'), got {type(mode).__name__}"
            )
        return self.get_mode(path) == mode

    def has_permissions(self, path: str | Path, permissions: str | int) -> bool:
        actual_mode = stat.S_IMODE(Path(path).stat().st_mode)
        expected_mode = self._normalize_permissions(permissions)
        return actual_mode == expected_mode

    def _normalize_permissions(self, permissions: str | int) -> int:
        if isinstance(permissions, int):
            return permissions

        if not isinstance(permissions, str):
            raise ValueError("Permissions must be int or string")

        permissions = permissions.strip()

        # Numeric form (supports 3 or 4 digit octal)
        if permissions.isdigit():
            return int(permissions, 8)

        # Symbolic form
        if len(permissions) != 9:
            raise ValueError(
                "Symbolic permissions must be 9 characters (e.g., 'rwxr-x---')"
            )

        perm_map = {"r": 4, "w": 2, "x": 1, "-": 0}

        mode = 0
        special = 0

        for idx in range(3):
            chunk = permissions[idx * 3 : (idx + 1) * 3]
            value = 0

            for pos, char in enumerate(chunk):
                if char in perm_map:
                    value += perm_map[char]

                elif pos == 2:
                    if idx == 0 and char in ("s", "S"):
                        special |= stat.S_ISUID
                        if char == "s":
                            value += 1

                    elif idx == 1 and char in ("s", "S"):
                        special |= stat.S_ISGID
                        if char == "s":
                            value += 1

                    elif idx == 2 and char in ("t", "T"):
                        special |= stat.S_ISVTX
                        if char == "t":
                            value += 1

                    else:
                        raise ValueError(f"Invalid permission character: {char}")

                else:
                    raise ValueError(f"Invalid permission character: {char}")

            mode = (mode << 3) | value

        return special | mode

    # ------------------------------------------------------------------
    # Access checks
    # ------------------------------------------------------------------

    def is_executable(self, path: str | Path) -> bool:
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return os.access(str(path), os.X_OK)

    def is_readable(self, path: str | Path) -> bool:
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return os.access(str(path), os.R_OK)

    def is_writable(self, path: str | Path) -> bool:
        if not Path(path).exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return os.access(str(path), os.W_OK)

    # ------------------------------------------------------------------
    # Size / ownership
    # ------------------------------------------------------------------

    def get_size(self, path: str | Path) -> int:
        return Path(path).stat().st_size

    def get_user(self, path: str | Path) -> str:
        stat_info = Path(path).stat()
        return pwd.getpwuid(stat_info.st_uid).pw_name

    def get_group(self, path: str | Path) -> str:
        stat_info = Path(path).stat()
        return grp.getgrgid(stat_info.st_gid).gr_name

    def get_owner(self, path: str | Path) -> Tuple[str, str]:
        return self.get_user(path), self.get_group(path)

    def is_owned_by_user(self, path: str | Path, user: str) -> bool:
        return self.get_user(path) == user

    def is_owned_by_group(self, path: str | Path, group: str) -> bool:
        return self.get_group(path) == group

    def is_owned_by(self, path: str | Path, user: str, group: str) -> bool:
        return self.get_user(path) == user and self.get_group(path) == group


@pytest.fixture
def file() -> File:
    return File()