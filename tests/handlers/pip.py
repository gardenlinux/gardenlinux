import os
import shutil

import pytest
from plugins.shell import ShellRunner


@pytest.fixture
def pip_requests(shell: ShellRunner):
    out = shell(
        '/bin/python3 -c "import site; print(site.getsitepackages()[0])"',
        capture_output=True,
    )
    package_dir = out.stdout.strip("\n")

    restore_backup = False
    if os.path.isdir(package_dir):
        restore_backup = True
        shutil.move(package_dir, package_dir + ".backup")

    delete_normalizer = not os.path.isfile("/usr/local/bin/normalizer")

    os.mkdir(package_dir)

    shell("/bin/pip3 install requests --break-system-packages --no-cache-dir")

    yield package_dir

    shutil.rmtree(package_dir)
    if restore_backup:
        shutil.move(package_dir + ".backup", package_dir)

    if delete_normalizer:
        os.remove("/usr/local/bin/normalizer")
