from helper.tests.garden_feat import garden_feat 
import pytest

@pytest.mark.parametrize(
    "test_case,config,input_features,output_features",
    [
        # Basic tests for positional cli args
        (
            "features",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"_dev": {'description': '_dev', 'type': 'flag'}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                  {"cloud": {'description': 'cloud', 'type': 'element'}}
            ],
            "base,kvm,_dev",
            "cloud,kvm,_slim,base,_dev"
        ),
        (
            "features",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"_dev": {'description': '_dev', 'type': 'flag'}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'exclude': ['cloud']}}},
                  {"cloud": {'description': 'cloud', 'type': 'element'}}
            ],
            "base,kvm,_dev",
            "kvm,_slim,base,_dev"
        ),
        (
            "features",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"_dev": {'description': '_dev', 'type': 'flag'}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'exclude': ['cloud']}}},
                  {"cloud": {'description': 'cloud', 'type': 'element', 'features': {'exclude': ['_ssh']}}},
                  {"_ssh": {'description': '_ssh', 'type': 'flag'}}
            ],
            "base,kvm,_dev",
            "kvm,_slim,base,_dev"
        ),
        (
            "cname",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"_dev": {'description': '_dev', 'type': 'flag'}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud', 'chost']}}},
                  {"cloud": {'description': 'cloud', 'type': 'element'}},
                  {"chost": {'description': 'chost', 'type': 'element'}}
            ],
            "kvm,_dev,chost",
            "kvm_dev"
        ),
        (
            "flags",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim', '_dev', 'firewall']}}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"cloud": {'description': 'cloud', 'type': 'element'}},
                  {"_dev": {'description': '_dev', 'type': 'flag'}},
                  {"firewall": {'description': 'firewall', 'type': 'flag'}}
            ],
            "base,kvm,_dev",
            "_slim,_dev,firewall"
        ),
        (
            "elements",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"cloud": {'description': 'cloud', 'type': 'element'}}
            ],
            "base,kvm",
            "cloud,kvm,base"
        ),
        (
            "ignore",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"cloud": {'description': 'cloud', 'type': 'element'}}
            ],
            "base,kvm",
            "garden-feat: warning: No feature is ignored."
        ),
        (
            "params",
            [
                  {"base": {'description': 'base', 'type': 'element', 'features': {'include': ['_slim']}}},
                  {"kvm": {'description': 'kvm', 'type': 'platform', 'features': {'include': ['cloud']}}},
                  {"server": {'description': 'server', 'type': 'element'}},
                  {"_slim": {'description': '_slim', 'type': 'flag'}},
                  {"cloud": {'description': 'cloud', 'type': 'element', 'features': {'include': ['server']}, 'fs': [{'dest': '/', 'type': 'ext4'}], 'disk': {'label': 'gpt', 'boot': ['mbr']}, 'convert': {'format': [{'type': 'raw'}]}}}
            ],
            "base,kvm",
            "raw"
        )
    ]
)


def test_garden_feat(test_case, config, input_features, output_features, local):
    garden_feat(test_case, config, input_features, output_features)
