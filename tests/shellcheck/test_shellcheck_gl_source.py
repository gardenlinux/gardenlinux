import logging
import glob
import os
import pytest
from pathlib import Path
from subprocess import PIPE, run

logger = logging.getLogger(__name__)


def is_bash_script(filepath):
    try:
        with open(filepath) as file:
          head = file.readline()
    except UnicodeDecodeError:
        return False # Ignore binary data
    if 'bash' in head:
        return True
    return False

def get_files_to_check(directory):
    all_files = Path(directory).glob('**/*')
    ret = list()
    for filename in all_files:
        if os.path.isfile(filename) and is_bash_script(filename):
            ret.append(filename)
    return ret


FILES_TO_CHECK = get_files_to_check('../')

@pytest.mark.parametrize('filepath', FILES_TO_CHECK)
def test_shellcheck_on_file(filepath):
    command = ['shellcheck','--severity=warning' , filepath]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    assert result.returncode==0, f"Shellcheck failed for file {filepath} \n {result.stderr} {result.stdout} "

