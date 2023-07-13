from helper.utils import check_file
import os
import pytest
import string

def files_excluded(client):
    files_to_be_excluded = []

    # get the list of excluded files from the current feature
    current = (os.getenv('PYTEST_CURRENT_TEST')).split('/')[0]
    path = f"/gardenlinux/features/{current}/file.exclude"
    try:
        with open(path) as f:
            files_to_be_excluded.append(f.read().splitlines)
    except OSError:
        pass

    # get an additional/optional list of files that must not be present in the image
    path = f"/gardenlinux/features/{current}/test/file.exclude.d/file.exclude.list"
    try:
        with open(path) as f:
            for file in f:
                file = file.strip(string.whitespace)
                # Skip comment lines
                if file.startswith("#"):
                    continue
                files_to_be_excluded.append(file)
    except OSError:
        pass

    if len(files_to_be_excluded) == 0:
        pytest.skip(f"Feature {current} does not require any files to be excluded.")

    actually_present = []
    for excluded_file in files_to_be_excluded:
        if check_file(client, excluded_file) is True:
            actually_present.append(excluded_file)

    assert len(actually_present) == 0, \
            f"{', '.join(actually_present)} must not be in the image but is actually present"
