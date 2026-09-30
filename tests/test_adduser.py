def test_adduser_system_uid_gid_range(parse_file):
    config = parse_file.parse("/etc/adduser.conf", format="keyval")

    assert config["FIRST_SYSTEM_UID"] == "101"
    assert config["FIRST_SYSTEM_GID"] == "101"
