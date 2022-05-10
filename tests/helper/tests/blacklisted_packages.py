import logging

from helper import utils

logger = logging.getLogger(__name__)

def blacklisted_packages(client, package):
    
    pkgslist = utils.get_package_list(client)

    assert not package in pkgslist, (f"{', '.join(package)} is " +
            "blacklisted, but installed")
