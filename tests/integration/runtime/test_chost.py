import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# chost Feature - Container Host Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-containerd-config",
    ]
)
@pytest.mark.feature("chost")
def test_chost_containerd_config_exists(file: File):
    """Test that containerd configuration exists"""
    assert file.is_regular_file(
        "/etc/containerd/config.toml"
    ), "Containerd configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-containerd-config",
    ]
)
@pytest.mark.feature("chost")
def test_chost_containerd_config_content(parse_file: ParseFile):
    """Test that containerd configuration contains the correct content"""
    config = parse_file.parse("/etc/containerd/config.toml")
    assert config["version"] == 2, "Containerd configuration should be version 2"
    assert (
        config["plugins"]["io.containerd.grpc.v1.cri"]["cni"]["bin_dir"]
        == "/var/lib/containerd/io.containerd.grpc.v1.cri.cni"
    ), "Containerd CNI bin directory should be /var/lib/containerd/io.containerd.grpc.v1.cri.cni"
    assert (
        config["plugins"]["io.containerd.grpc.v1.cri"]["containerd"]["runtimes"][
            "runc"
        ]["runtime_type"]
        == "io.containerd.runc.v2"
    ), "Containerd runc runtime type should be io.containerd.runc.v2"
    assert (
        config["plugins"]["io.containerd.grpc.v1.cri"]["containerd"]["runtimes"][
            "runc"
        ]["options"]["SystemdCgroup"]
        == True
    ), "Containerd runc runtime options should include SystemdCgroup"
    assert (
        config["plugins"]["io.containerd.internal.v1.opt"]["path"]
        == "/var/lib/containerd/io.containerd.internal.v1.opt"
    ), "Containerd internal opt path should be /var/lib/containerd/io.containerd.internal.v1.opt"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-crictl-yaml",
    ]
)
@pytest.mark.feature("chost")
def test_chost_crictl_config_exists(file: File):
    """Test that crictl configuration exists"""
    assert file.is_regular_file("/etc/crictl.yaml"), "Crictl configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-crictl-yaml",
    ]
)
@pytest.mark.feature("chost")
def test_chost_crictl_config_content(parse_file: ParseFile):
    """Test that crictl configuration contains the correct content"""
    config = parse_file.parse("/etc/crictl.yaml")
    assert (
        config["runtime-endpoint"] == "unix:///run/containerd/containerd.sock"
    ), "Crictl runtime endpoint should be unix:///run/containerd/containerd.sock"
    assert (
        config["image-endpoint"] == "unix:///run/containerd/containerd.sock"
    ), "Crictl image endpoint should be unix:///run/containerd/containerd.sock"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-service-containerd-override",
    ]
)
@pytest.mark.feature("chost")
def test_chost_containerd_service_override_exists(file: File):
    """Test that containerd service override exists"""
    assert file.exists(
        "/etc/systemd/system/containerd.service.d/override.conf"
    ), "Containerd service override should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-no-initd-apparmor",
    ]
)
@pytest.mark.feature("chost")
def test_chost_no_apparmor_init(file: File):
    """Test that chost does not have AppArmor init script"""
    assert not file.exists(
        "/etc/init.d/apparmor"
    ), "Container host should not have AppArmor init script"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-no-var-lib-containerd-opt",
    ]
)
@pytest.mark.feature("chost")
def test_chost_no_containerd_opt_directory(file: File):
    """Test that chost does not have containerd opt directory"""
    assert not file.exists(
        "/var/lib/containerd/opt"
    ), "Container host should not have containerd opt directory"
