from pyprctl import FileCaps
import pytest
from .shell import ShellRunner
from .find import Find, FIND_RESULT_TYPE_FILE


class Capabilities:
    def __init__(self, find: Find):
        self._find = find

    def list(self) -> list[str]:
        capabilities = []

        self._find.same_mnt_only = False
        self._find.root_path = "/"
        self._find.entry_type = FIND_RESULT_TYPE_FILE

        for f in self._find:
            c = self._get_capabilities(f)
            if c:
                capabilities.append(c)

        return capabilities

    def _get_capabilities(self, file_path: str) -> str | None:
        """Get file capabilities using pyprctl library.

        Uses pyprctl.FileCaps.get_for_file() to retrieve file capabilities
        and formats them to match getcap output format.
        """
        try:
            file_caps = FileCaps.get_for_file(file_path)
            if not file_caps or not file_caps.effective:
                return None

            # Format capabilities like getcap output
            capabilities = []
            for cap_name in file_caps.effective:
                cap_flags = []
                if file_caps.effective and cap_name in file_caps.effective:
                    cap_flags.append("e")
                if file_caps.permitted and cap_name in file_caps.permitted:
                    cap_flags.append("p")
                if file_caps.inheritable and cap_name in file_caps.inheritable:
                    cap_flags.append("i")

                if cap_flags:
                    capabilities.append(f"{cap_name}={''.join(cap_flags)}")

            return f"{file_path} {' '.join(capabilities)}" if capabilities else None

        except Exception:
            return None


@pytest.fixture
def capabilities(find: Find) -> Capabilities:
    return Capabilities(find)
