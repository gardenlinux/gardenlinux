import logging
import os
import re
import tempfile
from typing import List, Optional

import pefile
import pytest

from .kernel_versions import KernelVersions
from .shell import ShellRunner
from .utils import get_cname_from_os_release

logger = logging.getLogger(__name__)


class Initrd:
    """Inspect initrd contents using lsinitrd (dracut)."""

    def __init__(self, shell: ShellRunner, kernel_versions: KernelVersions):
        self._shell = shell
        installed = kernel_versions.get_installed()
        if not installed:
            self._kernel_version = None
            self._contents: List[str] = []
            return

        self._kernel_version = installed[0].version
        self._contents = self._load_initrd_contents(self._kernel_version)

    def _get_efi_path(self) -> Optional[str]:
        """Get the path to the EFI file based on CNAME from os-release.

        Returns:
            Path to EFI file, or None if CNAME not found or file doesn't exist.
        """
        cname = get_cname_from_os_release()
        if not cname:
            logger.debug("CNAME not found in /etc/os-release, cannot locate EFI file")
            return None

        efi_path = f"/efi/EFI/Linux/{cname}.efi"
        if not os.path.exists(efi_path):
            logger.debug(f"EFI file not found: {efi_path}")
            return None

        return efi_path

    def _get_initrd_section(
        self, pe: pefile.PE, efi_path: str
    ) -> Optional[pefile.SectionStructure]:
        """Find the .initrd section in a PE file.

        Args:
            pe: PE file object.
            efi_path: Path to EFI file (for logging).

        Returns:
            The .initrd section, or None if not found.
        """
        for section in pe.sections:
            # Section names are null-padded 8-byte strings
            section_name = section.Name.rstrip(b"\x00").decode("ascii", errors="ignore")
            if section_name == ".initrd":
                logger.debug(f"Found .initrd section in EFI file: {efi_path}")
                return section

        logger.warning(f"No .initrd section found in EFI file: {efi_path}")
        return None

    def _get_initrd_data(
        self, initrd_section: pefile.SectionStructure, efi_path: str
    ) -> Optional[bytes]:
        """Extract data from the .initrd section.

        Args:
            initrd_section: The .initrd section from the PE file.
            efi_path: Path to EFI file (for logging).

        Returns:
            The section data, or None if empty.
        """
        initrd_data = initrd_section.get_data()
        if not initrd_data or len(initrd_data) == 0:
            logger.warning(f".initrd section is empty in EFI file: {efi_path}")
            return None

        return initrd_data

    def _write_initrd_to_temp_file(self, initrd_data: bytes, efi_path: str) -> str:
        """Write initrd data to a temporary file.

        Args:
            initrd_data: The initrd data to write.
            efi_path: Path to EFI file (for logging).

        Returns:
            Path to the temporary file.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".img") as tmp_file:
            tmp_file.write(initrd_data)
            tmp_path = tmp_file.name

        logger.info(
            f"Extracted initrd from EFI file {efi_path} to {tmp_path} "
            f"({len(initrd_data)} bytes)"
        )
        return tmp_path

    def _extract_initrd_from_efi(self) -> Optional[str]:
        """Extract initrd from EFI file for trustedboot/USI flavors.

        The initrd is embedded in the EFI file as a PE32+ section named '.initrd'.

        Returns:
            Path to extracted initrd file, or None if extraction fails.
        """
        efi_path = self._get_efi_path()
        if not efi_path:
            return None

        try:
            logger.debug(f"Loading EFI file: {efi_path}")
            pe = pefile.PE(efi_path, fast_load=True)

            initrd_section = self._get_initrd_section(pe, efi_path)
            if not initrd_section:
                return None

            initrd_data = self._get_initrd_data(initrd_section, efi_path)
            if not initrd_data:
                return None

            return self._write_initrd_to_temp_file(initrd_data, efi_path)

        except pefile.PEFormatError as e:
            logger.warning(f"Invalid PE format in EFI file {efi_path}: {e}")
            return None
        except (OSError, IOError) as e:
            logger.warning(f"Error reading EFI file {efi_path}: {e}")
            return None
        except Exception as e:
            logger.warning(
                f"Unexpected error extracting initrd from EFI file {efi_path}: {e}"
            )
            return None

    def _load_initrd_contents(self, kernel_version: str) -> List[str]:
        """Load initrd contents for the given kernel version.

        Tries EFI file first (for trustedboot/USI flavors), then falls back to
        regular initrd file.

        Args:
            kernel_version: Kernel version string.

        Returns:
            List of file paths found in the initrd.

        Raises:
            RuntimeError: If neither EFI initrd nor legacy initrd can be found.
        """
        initrd_path = None
        extracted_path = None

        # Try EFI file first (for trustedboot/USI)
        extracted_path = self._extract_initrd_from_efi()
        if extracted_path:
            initrd_path = extracted_path
            logger.debug(f"Using initrd extracted from EFI file: {initrd_path}")
        else:
            # Fall back to legacy initrd file
            legacy_path = f"/boot/initrd.img-{kernel_version}"
            if os.path.exists(legacy_path):
                initrd_path = legacy_path
                logger.debug(f"Using legacy initrd file: {initrd_path}")
            else:
                logger.debug(f"Legacy initrd file not found: {legacy_path}")

        if not initrd_path:
            raise RuntimeError(
                f"Could not find initrd for kernel {kernel_version}. "
                "Neither EFI initrd extraction nor legacy initrd file available."
            )

        try:
            logger.debug(f"Executing: lsinitrd {initrd_path}")
            result = self._shell(
                f"lsinitrd {initrd_path}",
                capture_output=True,
                ignore_exit_code=True,
            )

            if result.returncode == 0:
                contents = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
                logger.debug(f"lsinitrd output for {initrd_path}:\n{result.stdout}")
                logger.info(f"Found {len(contents)} files in initrd {initrd_path}")
                return contents

            logger.warning(
                f"lsinitrd failed for {initrd_path} with exit code {result.returncode}"
            )
            if result.stderr:
                logger.warning(f"lsinitrd stderr: {result.stderr}")
            raise RuntimeError(
                f"lsinitrd failed for {initrd_path} with exit code {result.returncode}"
            )
        finally:
            # Clean up extracted temporary file
            if extracted_path and os.path.exists(extracted_path):
                try:
                    os.unlink(extracted_path)
                    logger.debug(f"Cleaned up temporary initrd file: {extracted_path}")
                except OSError as e:
                    logger.warning(
                        f"Failed to clean up temporary file {extracted_path}: {e}"
                    )

    def _get_contents(self, kernel_version: Optional[str] = None) -> List[str]:
        """Get all files in the initrd.

        Args:
            kernel_version: Kernel version string. If None, uses the first installed kernel.

        Returns:
            List of file paths found in the initrd.
        """
        if kernel_version is None:
            return self._contents
        else:
            # Load contents for a different kernel version
            return self._load_initrd_contents(kernel_version)

    def contains_module(
        self, module_name: str, kernel_version: Optional[str] = None
    ) -> bool:
        """Check if a kernel module is present in the initrd.

        Args:
            module_name: Name of the module to check (e.g., "nvme", "nvme-core").
            kernel_version: Kernel version string. If None, uses the first installed kernel.

        Returns:
            True if the module is found in the initrd.
        """
        if kernel_version is None:
            kernel_version = self._kernel_version
        contents = self._get_contents(kernel_version)
        if not contents:
            return False

        pattern = re.compile(
            # (usr/)?lib/modules/         # Optionally starts with 'usr/', then 'lib/modules/', does not match the start of the line as lsinitrd outputs ls -l format with path at the end
            # {kernel_version}/           # Kernel version directory (e.g., '6.12.47-cloud-amd64/')
            # kernel/                     # Must have 'kernel/' next
            # (?:[^/]+/)*                 # One or more directories, matches nested subdirectories (e.g., drivers/net/)
            # {module_name}\.ko           # The target module file, as {module_name}.ko (escaped for regex safety)
            # (\.(xz|zst))?               # Optionally followed by compression extensions '.xz' or '.zst'
            # $                           # End of string (ensures no suffix)
            rf"(usr/)?lib/modules/{kernel_version}/kernel/(?:[^/]+/)*{re.escape(module_name)}\.ko(\.(xz|zst))?$"
        )
        return any(pattern.search(entry) for entry in contents)

    def contains_file(
        self, file_path: str, kernel_version: Optional[str] = None
    ) -> bool:
        """Check if a specific file path is present in the initrd.

        Args:
            file_path: Path to check within initrd (e.g., "usr/sbin/fsck").
            kernel_version: Kernel version string. If None, uses the first installed kernel.

        Returns:
            True if the file is found in the initrd.
        """
        if kernel_version is None:
            kernel_version = self._kernel_version
        contents = self._get_contents(kernel_version)
        return file_path in contents or any(
            entry.endswith(file_path) for entry in contents
        )

    def list_modules(self, kernel_version: Optional[str] = None) -> List[str]:
        """List all kernel modules present in the initrd.

        Args:
            kernel_version: Kernel version string. If None, uses the first installed kernel.

        Returns:
            List of module paths found in the initrd.
        """
        if kernel_version is None:
            kernel_version = self._kernel_version
        contents = self._get_contents(kernel_version)
        if not contents:
            return []

        pattern = re.compile(
            # (usr/)?lib/modules/         # Optionally starts with 'usr/', then 'lib/modules/', does not match the start of the line as lsinitrd outputs ls -l format with path at the end
            # {kernel_version}/            # Kernel version directory (e.g., '6.12.47-cloud-amd64/')
            # kernel/                     # Must have 'kernel/' next
            # (?:[^/]+/)*                 # One or more directories, matches nested subdirectories (e.g., drivers/net/)
            # \.ko                        # The target module file, as .ko (escaped for regex safety)
            # (\.(xz|zst))?               # Optionally followed by compression extensions '.xz' or '.zst'
            # $                           # End of string (ensures no suffix)
            rf"(usr/)?lib/modules/{kernel_version}/kernel/(?:[^/]+/)*\.ko(\.(xz|zst))?$"
        )
        modules = [entry for entry in contents if pattern.search(entry)]
        return modules


@pytest.fixture
def initrd(shell: ShellRunner, kernel_versions: KernelVersions) -> Initrd:
    """Fixture providing access to initrd inspection functionality."""
    return Initrd(shell, kernel_versions)
