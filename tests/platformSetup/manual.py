from helper.sshclient import RemoteClient

class Manual:
    """Handle Manual Instance"""

    @classmethod
    def fixture(cls, config):

        try:
            ssh = None
            ssh = RemoteClient(
                host=config["host"],
                sshconfig=config["ssh"],
                wait_for_systemd=True
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
