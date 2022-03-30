from codecs import ignore_errors
from curses import ERR
from distutils.log import ERROR
import logging
import glob
import os
import pytest
import re

from pathlib import Path
from subprocess import PIPE, run
from itertools import filterfalse

logger = logging.getLogger(__name__)

SKIP_COMMENT = "skip-shellcheck"


def is_bash_script(filepath):
    try:
        with open(filepath) as file:
            head = file.readline()
    except UnicodeDecodeError:
        return False  # Ignore binary data
    if 'bash' in head:
        return True
    return False


def has_skip_comment(filepath):
    fp = open(filepath)
    ret = False
    for i, line in enumerate(fp):
        if i == 1:
            if SKIP_COMMENT in line:
                ret = True
                break
        if i > 1:
            break

    fp.close()
    return ret


def get_ignore_list(ignore_path):
    ret = list()
    if not os.path.isfile(ignore_path):
        logger.warn(f"File {ignore_path} does not exist")
        return ret
    with open(ignore_path) as file:
        for line in file.readlines():
            if not line:
                continue
            if line.isspace():
                continue
            if line.startswith('#'):
                continue
            ret.append(line.rstrip())
    return ret


def is_file_ignored(filename, ignore_list):
    for ignore_expression in ignore_list:
        if not ignore_expression:
            continue
        if ignore_expression.isspace():
            continue
        if ignore_expression.startswith('#'):
            continue
        regex = rf"\.\.\/" + re.escape(ignore_expression) + ".*"
        if re.search(regex, str(filename), re.IGNORECASE):
            return True
    return False


def apply_ignore_filter(ignore_list, all_list):

    filtered_list = \
        [file for file in all_list if not is_file_ignored(file, ignore_list)]

    return filtered_list


def get_files_to_check(directory):
    all_files = Path(directory).glob('**/*')
    ret = list()
    for filename in all_files:
        if os.path.isfile(filename) and is_bash_script(filename):
            if not has_skip_comment(filename):
                ret.append(filename)
    return ret


FILES_TO_CHECK = \
    apply_ignore_filter(
            get_ignore_list(Path(os.getcwd() + '/shellcheck/file.ignore')),
            get_files_to_check('..')
        )

ERRORS_TO_IGNORE = \
    get_ignore_list(Path(os.getcwd() + '/shellcheck/error.ignore'))


@pytest.mark.parametrize('filepath', FILES_TO_CHECK)
def test_shellcheck_on_file(severity_level, filepath):
    command = ['shellcheck']

    for err in ERRORS_TO_IGNORE:
        command.append('--exclude')
        command.append(err)
    command.append(f"--severity={severity_level}")
    command.append(filepath)

    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    assert result.returncode == 0, \
        f"Shellcheck failed on: {filepath} \n {result.stderr} {result.stdout} "
