import logging
import os
import sys
from pathlib import Path

import yaml

from platformSetup.gcp import GCP

logger = logging.getLogger(__name__)

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


def config():
    try:
        root = Path(os.path.dirname(os.path.abspath(__file__)))
        path = root.joinpath("./test_config.yaml")
        with open(path) as f:
            options = yaml.load(f, Loader=yaml.FullLoader)
    except OSError as e:
        logger.exception(e)
        exit(1)
    return options


def main():
    c = config()
    gcp_config = c["gcp"]
    instances = GCP.fixture(gcp_config)
    logger.info(f"{instances}")


if __name__ == "__main__":
    main()
