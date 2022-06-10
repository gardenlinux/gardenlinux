from helper.tests.orphaned import orphaned


def test_orphaned(client):
    orphaned(client)
