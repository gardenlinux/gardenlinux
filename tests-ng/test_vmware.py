import pytest
import os
from plugins.file_content import file_content

file = [ "/etc/cloud/cloud.cfg" ] 
args = [ "ntp",
         "resizefs",
         "growpart",
        ]

@pytest.mark.feature("vmware")
@pytest.mark.parametrize("filename", file)
@pytest.mark.parametrize("content", args)

def test_file_content(filename: str, content: str):
    if os.path.isfile(filename):
        if (file_content(filename, content)):
            assert False, f"Found {content} in {filename} which is not expected."
    else:
        assert False, "File does not exist"
