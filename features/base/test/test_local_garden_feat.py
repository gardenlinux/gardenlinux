from helper.tests.garden_feat import garden_feat 
import pytest

@pytest.mark.parametrize(
    "test_case,config",
    [
        # Basic tests for positional cli args
        ("features", [
                      {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                      {"_slim": {'description': '_slim', 'type': 'flag'}},
                      {"_dev": {'description': '_dev', 'type': 'flag'}},
                      {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                      {"cloud": {'description': 'cloud', 'type': 'element'}}
                     ]
        ),
        ("cname", [
                      {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                      {"_slim": {'description': '_slim', 'type': 'flag'}},
                      {"_dev": {'description': '_dev', 'type': 'flag'}},
                      {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                      {"cloud": {'description': 'cloud', 'type': 'element'}}
                     ]
        ),
        ("flags", [
                      {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim', '_dev', 'firewall']}}},
                      {"_slim": {'description': '_slim', 'type': 'flag'}},
                      {"cloud": {'description': 'cloud', 'type': 'element'}},
                      {"_dev": {'description': '_dev', 'type': 'flag'}},
                      {"firewall": {'description': 'firewall', 'type': 'flag'}}
                     ]
        ),
        ("elements", [
                      {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                      {"cloud": {'description': 'cloud', 'type': 'element'}},
                      {"_slim": {'description': '_slim', 'type': 'flag'}},
                     ]
        ),
        ("ignore", [
                      {"base": {'description': 'base', 'type': 'element', 'features': {'exclude': ['_slim', 'cloud']}}},
                      {"cloud": {'description': 'cloud', 'type': 'element'}},
                      {"_slim": {'description': '_slim', 'type': 'flag'}}
                     ]
        ),
        # Exclude tests for features
        ("exclude_features", [
                      {"base": {'description': 'base', 'type': 'element', 'features': {'exclude': ['_slim']}}},
                      {"cloud": {'description': 'cloud', 'type': 'element'}},
                      {"_slim": {'description': '_slim', 'type': 'flag'}}
                     ]
        ),
        # Param JSON export
        ("params", [
                      {"cloud": {'description': 'cloud', 'type': 'element', 'features': {'include': ['server']}, 'fs': [{'dest': '/', 'type': 'ext4'}], 'disk': {'label': 'gpt', 'boot': ['mbr']}, 'convert': {'format': [{'type': 'raw'}]}}},
                      {"server": {'description': 'server', 'type': 'element'}}
                     ]
        )
    ]
)


def test_garden_feat(client, test_case, config, chroot):
    garden_feat(client, test_case, config)
