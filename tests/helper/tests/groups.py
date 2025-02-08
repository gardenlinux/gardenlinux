from helper.utils import execute_remote_command


def groups(client, test_group, test_user):
    """ Test """
    # Get group info from remote platform
    cmd = "getent group"
    out = execute_remote_command(client, cmd)
    users = []

    # Process output
    for line in out.split("\n"):
        # Split line by ":"
        line_split = line.split(":")
        # First part is our group
        group = line_split[0]
        if group == test_group:
            # Get user(s) of group
            users = line_split[3].split(",")

    # Check if user is legitimated for the group
    for user in users:
        if user != "":
            assert user in test_user, f"User {user} is not allowed part of group {test_group}."
