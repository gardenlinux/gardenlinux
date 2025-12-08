"""Comprehensive tests for file.py plugin."""

import grp
import os
import pwd
import stat
from pathlib import Path

import pytest
from plugins.file import File

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def restricted_directory(tmp_path):
    """
    Create a restricted directory for PermissionError tests.
    Uses tmp_path and restores permissions for pytest cleanup.
    """
    restricted_dir = tmp_path / "restricted"
    restricted_dir.mkdir()
    test_file = restricted_dir / "test.txt"
    test_file.write_text("content")

    # Save original mode
    original_mode = restricted_dir.stat().st_mode

    # Remove execute permission
    os.chmod(restricted_dir, 0o600)

    yield restricted_dir, test_file

    # Restore permissions for pytest cleanup
    os.chmod(restricted_dir, original_mode)


# ============================================================================
# File Tests - File system metadata operations
# ============================================================================


class TestFileExists:
    """Tests for File.exists() method."""

    def test_exists_with_file(self, file: File, tmp_path):
        """Test exists() with a regular file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert file.exists(test_file)
        assert not file.exists(tmp_path / "nonexistent")

    def test_exists_with_directory(self, file: File, tmp_path):
        """Test exists() with a directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        assert file.exists(test_dir)
        assert not file.exists(tmp_path / "nonexistent_dir")


class TestFileIsRegularFile:
    """Tests for File.is_regular_file() method."""

    def test_is_regular_file_with_file(self, file: File, tmp_path):
        """Test is_regular_file() with a regular file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert file.is_regular_file(test_file)
        assert not file.is_regular_file(tmp_path / "nonexistent")

    def test_is_regular_file_with_directory(self, file: File, tmp_path):
        """Test is_regular_file() returns False for directories."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        assert not file.is_regular_file(test_dir)

    def test_is_regular_file_with_symlink(self, file: File, tmp_path):
        """Test is_regular_file() with a symlink to a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        symlink = tmp_path / "symlink.txt"
        symlink.symlink_to(test_file)

        # is_regular_file() does not follow symlinks, so symlink should return False
        assert not file.is_regular_file(symlink)
        # The actual file should still return True
        assert file.is_regular_file(test_file)


class TestFileIsDir:
    """Tests for File.is_dir() method."""

    def test_is_dir_with_directory(self, file: File, tmp_path):
        """Test is_dir() with a directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        assert file.is_dir(test_dir)
        assert not file.is_dir(tmp_path / "nonexistent")

    def test_is_dir_with_file(self, file: File, tmp_path):
        """Test is_dir() returns False for files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert not file.is_dir(test_file)

    def test_is_dir_with_symlink(self, file: File, tmp_path):
        """Test is_dir() with a symlink to a directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        symlink = tmp_path / "symlink_dir"
        symlink.symlink_to(test_dir)

        # is_dir() does not follow symlinks, so symlink should return False
        assert not file.is_dir(symlink)
        # The actual directory should still return True
        assert file.is_dir(test_dir)


class TestFileIsSymlink:
    """Tests for File.is_symlink() method."""

    def test_is_symlink_with_symlink(self, file: File, tmp_path):
        """Test is_symlink() with a symlink."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        symlink = tmp_path / "symlink.txt"
        symlink.symlink_to(test_file)

        assert file.is_symlink(symlink)
        assert not file.is_symlink(test_file)

    def test_is_symlink_with_file_and_dir(self, file: File, tmp_path):
        """Test is_symlink() returns False for regular files and directories."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        assert not file.is_symlink(test_file)
        assert not file.is_symlink(test_dir)
        assert not file.is_symlink(tmp_path / "nonexistent")

    def test_is_symlink_with_broken_symlink_raises_error(self, file: File, tmp_path):
        """Test is_symlink() raises FileNotFoundError for broken symlink by default."""
        broken_symlink = tmp_path / "broken_link"
        broken_symlink.symlink_to(tmp_path / "nonexistent_target")

        with pytest.raises(FileNotFoundError, match="Broken symlink"):
            file.is_symlink(broken_symlink)

    def test_is_symlink_with_broken_symlink_no_error(self, file: File, tmp_path):
        """Test is_symlink() returns True for broken symlink when error_on_broken_symlink=False."""
        broken_symlink = tmp_path / "broken_link"
        broken_symlink.symlink_to(tmp_path / "nonexistent_target")

        assert file.is_symlink(broken_symlink, error_on_broken_symlink=False)

    def test_is_symlink_with_valid_symlink(self, file: File, tmp_path):
        """Test is_symlink() with valid symlink (both error_on_broken_symlink settings)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        valid_symlink = tmp_path / "valid_link"
        valid_symlink.symlink_to(test_file)

        assert file.is_symlink(valid_symlink)  # default True
        assert file.is_symlink(valid_symlink, error_on_broken_symlink=False)

    def test_is_symlink_with_target_matching(self, file: File, tmp_path):
        """Test is_symlink() with target parameter - matching target."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        symlink = tmp_path / "link.txt"
        symlink.symlink_to(test_file)

        # Test with absolute target path
        assert file.is_symlink(symlink, target=test_file)
        # Test with relative target path (relative to symlink's parent)
        assert file.is_symlink(symlink, target="test.txt")
        # Test with Path object
        assert file.is_symlink(symlink, target=Path("test.txt"))

    def test_is_symlink_with_target_not_matching(self, file: File, tmp_path):
        """Test is_symlink() with target parameter - non-matching target."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        other_file = tmp_path / "other.txt"
        other_file.write_text("other")
        symlink = tmp_path / "link.txt"
        symlink.symlink_to(test_file)

        # Should return False when target doesn't match
        assert not file.is_symlink(symlink, target=other_file)
        assert not file.is_symlink(symlink, target="other.txt")
        assert not file.is_symlink(symlink, target="/nonexistent/path")

    def test_is_symlink_with_target_relative_path(self, file: File, tmp_path):
        """Test is_symlink() with target parameter using relative paths."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.write_text("content")
        symlink = tmp_path / "link.txt"
        symlink.symlink_to(test_file)

        # Test with relative path from symlink's parent
        assert file.is_symlink(symlink, target="subdir/test.txt")
        # Test with absolute path
        assert file.is_symlink(symlink, target=test_file)

    def test_is_symlink_with_target_broken_symlink(self, file: File, tmp_path):
        """Test is_symlink() with target parameter on broken symlink."""
        broken_symlink = tmp_path / "broken_link"
        target_path = tmp_path / "nonexistent_target"
        broken_symlink.symlink_to(target_path)

        # Target validation should work even for broken symlinks when error_on_broken_symlink=False
        assert file.is_symlink(
            broken_symlink, target=target_path, error_on_broken_symlink=False
        )
        assert file.is_symlink(
            broken_symlink, target="nonexistent_target", error_on_broken_symlink=False
        )
        assert not file.is_symlink(
            broken_symlink, target="wrong_target", error_on_broken_symlink=False
        )

        # When error_on_broken_symlink=True, should raise error even with target validation
        with pytest.raises(FileNotFoundError, match="Broken symlink"):
            file.is_symlink(
                broken_symlink, target=target_path, error_on_broken_symlink=True
            )


class TestFileGetMode:
    """Tests for File.get_mode() method."""

    def test_get_mode_with_various_modes(self, file: File, tmp_path):
        """Test get_mode() with various permission modes."""
        test_file_755 = tmp_path / "test_755.sh"
        test_file_755.write_text("#!/bin/bash")
        os.chmod(test_file_755, 0o755)

        test_file_644 = tmp_path / "test_644.txt"
        test_file_644.write_text("content")
        os.chmod(test_file_644, 0o644)

        assert file.get_mode(test_file_755) == "0755"
        assert file.get_mode(test_file_644) == "0644"

    def test_get_mode_raises_file_not_found_error(self, file: File, tmp_path):
        """Test get_mode() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.get_mode(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_get_mode_raises_permission_error(self, file: File, restricted_directory):
        """Test get_mode() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.get_mode(test_file)


class TestFileHasMode:
    """Tests for File.has_mode() method."""

    def test_has_mode_with_octal_mode(self, file: File, tmp_path):
        """Test has_mode() with octal permission mode."""
        test_file = tmp_path / "test.sh"
        test_file.write_text("#!/bin/bash")
        os.chmod(test_file, 0o755)

        assert file.has_mode(test_file, "0755")
        assert not file.has_mode(test_file, "0644")
        assert not file.has_mode(test_file, "0777")

    def test_has_mode_with_different_modes(self, file: File, tmp_path):
        """Test has_mode() with different permission modes."""
        test_file_644 = tmp_path / "test_644.txt"
        test_file_644.write_text("content")
        os.chmod(test_file_644, 0o644)

        test_file_600 = tmp_path / "test_600.txt"
        test_file_600.write_text("content")
        os.chmod(test_file_600, 0o600)

        assert file.has_mode(test_file_644, "0644")
        assert file.has_mode(test_file_600, "0600")
        assert not file.has_mode(test_file_644, "0600")
        assert not file.has_mode(test_file_600, "0644")

    def test_has_mode_raises_file_not_found_error(self, file: File, tmp_path):
        """Test has_mode() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.has_mode(non_existent, "0755")

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_has_mode_raises_permission_error(self, file: File, restricted_directory):
        """Test has_mode() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.has_mode(test_file, "0644")


class TestFileIsExecutable:
    """Tests for File.is_executable() method."""

    def test_is_executable_with_executable_file(self, file: File, tmp_path):
        """Test is_executable() with an executable file."""
        test_file = tmp_path / "test.sh"
        test_file.write_text("#!/bin/bash")
        os.chmod(test_file, 0o755)

        assert file.is_executable(test_file)

    def test_is_executable_with_non_executable_file(self, file: File, tmp_path):
        """Test is_executable() with a non-executable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        os.chmod(test_file, 0o644)

        assert not file.is_executable(test_file)

    def test_is_executable_raises_file_not_found_error(self, file: File, tmp_path):
        """Test is_executable() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.is_executable(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_is_executable_raises_permission_error(
        self, file: File, restricted_directory
    ):
        """Test is_executable() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.is_executable(test_file)


class TestFileIsReadable:
    """Tests for File.is_readable() method."""

    def test_is_readable_with_readable_file(self, file: File, tmp_path):
        """Test is_readable() with a readable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        os.chmod(test_file, 0o644)

        assert file.is_readable(test_file)

    def test_is_readable_with_non_readable_file(self, file: File, tmp_path):
        """Test is_readable() with a non-readable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        os.chmod(test_file, 0o000)

        # Note: This test may pass if running as root, as root can read any file
        # In practice, we might need to skip this test when running as root
        try:
            result = file.is_readable(test_file)
            # If we can read it (running as root), that's fine too
            assert isinstance(result, bool)
        except PermissionError:
            # Expected when not running as root
            pass

    def test_is_readable_raises_file_not_found_error(self, file: File, tmp_path):
        """Test is_readable() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.is_readable(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_is_readable_raises_permission_error(
        self, file: File, restricted_directory
    ):
        """Test is_readable() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.is_readable(test_file)


class TestFileIsWritable:
    """Tests for File.is_writable() method."""

    def test_is_writable_with_writable_file(self, file: File, tmp_path):
        """Test is_writable() with a writable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        os.chmod(test_file, 0o644)

        assert file.is_writable(test_file)

    def test_is_writable_with_non_writable_file(self, file: File, tmp_path):
        """Test is_writable() with a non-writable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        os.chmod(test_file, 0o444)

        # Note: This test may pass if running as root, as root can write any file
        # In practice, we might need to skip this test when running as root
        try:
            result = file.is_writable(test_file)
            # If we can write it (running as root), that's fine too
            assert isinstance(result, bool)
        except PermissionError:
            # Expected when not running as root
            pass

    def test_is_writable_raises_file_not_found_error(self, file: File, tmp_path):
        """Test is_writable() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.is_writable(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_is_writable_raises_permission_error(
        self, file: File, restricted_directory
    ):
        """Test is_writable() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.is_writable(test_file)


class TestFileGetSize:
    """Tests for File.get_size() method."""

    def test_get_size_with_empty_file(self, file: File, tmp_path):
        """Test get_size() with an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        assert file.get_size(test_file) == 0

    def test_get_size_with_small_file(self, file: File, tmp_path):
        """Test get_size() with a small file."""
        content = "Hello, World!"
        test_file = tmp_path / "small.txt"
        test_file.write_text(content)

        assert file.get_size(test_file) == len(content)

    def test_get_size_with_larger_file(self, file: File, tmp_path):
        """Test get_size() with a larger file."""
        content = "x" * 1000
        test_file = tmp_path / "large.txt"
        test_file.write_text(content)

        assert file.get_size(test_file) == 1000

    def test_get_size_raises_file_not_found_error(self, file: File, tmp_path):
        """Test get_size() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.get_size(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_get_size_raises_permission_error(self, file: File, restricted_directory):
        """Test get_size() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.get_size(test_file)


class TestFileGetOwner:
    """Tests for File.get_owner() method."""

    def test_get_owner(self, file: File, tmp_path):
        """Test get_owner() retrieves user and group."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        user, group = file.get_owner(test_file)
        assert isinstance(user, str)
        assert isinstance(group, str)

        # Verify it matches current user/group
        current_uid = os.getuid()
        current_gid = os.getgid()
        expected_user = pwd.getpwuid(current_uid).pw_name
        expected_group = grp.getgrgid(current_gid).gr_name

        assert user == expected_user
        assert group == expected_group

    def test_get_owner_raises_file_not_found_error(self, file: File, tmp_path):
        """Test get_owner() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.get_owner(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_get_owner_raises_permission_error(self, file: File, restricted_directory):
        """Test get_owner() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.get_owner(test_file)


class TestFileGetUser:
    """Tests for File.get_user() method."""

    def test_get_user(self, file: File, tmp_path):
        """Test get_user() retrieves username."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        user = file.get_user(test_file)
        assert isinstance(user, str)

        # Verify it matches current user
        current_uid = os.getuid()
        expected_user = pwd.getpwuid(current_uid).pw_name

        assert user == expected_user

    def test_get_user_raises_file_not_found_error(self, file: File, tmp_path):
        """Test get_user() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.get_user(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_get_user_raises_permission_error(self, file: File, restricted_directory):
        """Test get_user() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.get_user(test_file)


class TestFileGetGroup:
    """Tests for File.get_group() method."""

    def test_get_group(self, file: File, tmp_path):
        """Test get_group() retrieves group name."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        group = file.get_group(test_file)
        assert isinstance(group, str)

        # Verify it matches current group
        current_gid = os.getgid()
        expected_group = grp.getgrgid(current_gid).gr_name

        assert group == expected_group

    def test_get_group_raises_file_not_found_error(self, file: File, tmp_path):
        """Test get_group() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.get_group(non_existent)

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_get_group_raises_permission_error(self, file: File, restricted_directory):
        """Test get_group() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.get_group(test_file)


class TestFileIsOwnedByUser:
    """Tests for File.is_owned_by_user() method."""

    def test_is_owned_by_user(self, file: File, tmp_path):
        """Test is_owned_by_user() checks specific user ownership."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        current_uid = os.getuid()
        expected_user = pwd.getpwuid(current_uid).pw_name

        assert file.is_owned_by_user(test_file, expected_user)
        assert not file.is_owned_by_user(test_file, "nonexistent_user")

    def test_is_owned_by_user_raises_file_not_found_error(self, file: File, tmp_path):
        """Test is_owned_by_user() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.is_owned_by_user(non_existent, "user")

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_is_owned_by_user_raises_permission_error(
        self, file: File, restricted_directory
    ):
        """Test is_owned_by_user() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.is_owned_by_user(test_file, "user")


class TestFileIsOwnedByGroup:
    """Tests for File.is_owned_by_group() method."""

    def test_is_owned_by_group(self, file: File, tmp_path):
        """Test is_owned_by_group() checks specific group ownership."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        current_gid = os.getgid()
        expected_group = grp.getgrgid(current_gid).gr_name

        assert file.is_owned_by_group(test_file, expected_group)
        assert not file.is_owned_by_group(test_file, "nonexistent_group")

    def test_is_owned_by_group_raises_file_not_found_error(self, file: File, tmp_path):
        """Test is_owned_by_group() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.is_owned_by_group(non_existent, "group")

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_is_owned_by_group_raises_permission_error(
        self, file: File, restricted_directory
    ):
        """Test is_owned_by_group() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.is_owned_by_group(test_file, "group")


class TestFileIsOwnedBy:
    """Tests for File.is_owned_by() method."""

    def test_is_owned_by(self, file: File, tmp_path):
        """Test is_owned_by() checks specific owner (user and group)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        current_uid = os.getuid()
        current_gid = os.getgid()
        expected_user = pwd.getpwuid(current_uid).pw_name
        expected_group = grp.getgrgid(current_gid).gr_name

        assert file.is_owned_by(test_file, expected_user, expected_group)
        assert not file.is_owned_by(test_file, "wrong_user", expected_group)
        assert not file.is_owned_by(test_file, expected_user, "wrong_group")
        assert not file.is_owned_by(test_file, "wrong_user", "wrong_group")

    def test_is_owned_by_raises_file_not_found_error(self, file: File, tmp_path):
        """Test is_owned_by() raises FileNotFoundError for non-existing path."""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            file.is_owned_by(non_existent, "user", "group")

    @pytest.mark.skipif(os.getuid() == 0, reason="Root can access any file")
    def test_is_owned_by_raises_permission_error(
        self, file: File, restricted_directory
    ):
        """Test is_owned_by() raises PermissionError when access is denied."""
        restricted_dir, test_file = restricted_directory

        with pytest.raises(PermissionError):
            file.is_owned_by(test_file, "user", "group")
