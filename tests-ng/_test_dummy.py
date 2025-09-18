import pytest

def test_always_pass():
    assert True

@pytest.mark.feature("nonExistingFeature")
def test_feature_never():
    assert False

@pytest.mark.feature("base")
def test_feature_base():
    assert True

@pytest.mark.feature("(cloud or metal) and not _usi")
def test_rootfs_ext4_options():
    # perform some check here
    pass

@pytest.mark.root
def test_root_user(shell):
    assert shell("id -u", capture_output=True).stdout.strip() == "0"

def test_regular_user(shell):
    assert shell("id -u", capture_output=True).stdout.strip() != "0"

def test_shell_print(shell):
    shell("echo abc")
    shell("echo abc >&2")

def test_shell_fail(shell):
    shell("echo hello; false; echo abc")

def test_print():
    print("hello")

@pytest.mark.booted
def test_only_if_booted():
    assert True

def test_sysctl(sysctl):
    assert sysctl["net.ipv4.conf.all.rp_filter"] != 1
    assert sysctl["net.ipv4.conf.default.rp_filter"] != 1


@pytest.mark.modify
def test_modify_state(shell):
    shell("echo hello > /tmp/hello.txt")
    print(shell("ls -l /tmp/hello.txt", capture_output=True))
