import os
import yaml
import json
import tempfile
from helper import utils


def garden_feat(client, test_case, config):
    """Check the MD5 sums of installed Debian packages"""

    # Run tests for cli opt "features"
    if test_case == "features":
        # Define feature set to test
        features = "base,kvm,_dev"
        val_ok = "_dev,_slim,base,cloud,kvm"
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "cname":
        # Define feature set to test
        features = "base,kvm,_dev"
        val_ok = "kvm_dev"
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "flags":
        # Define feature set to test
        features = "base,cloud"
        val_ok = "_dev,_slim,firewall"
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "elements":
        # Define feature set to test
        features = "base,cloud"
        val_ok = "base,cloud"
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "ignore":
        # Define feature set to test
        features = "base"
        val_ok = ""
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "exclude_features":
        # Overwrite "test_case" to fake "features"
        test_case = "features"
        # Define feature set to test
        features = "base,cloud"
        val_ok = "base,cloud"
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "exclude_features":
        # Overwrite "test_case" to fake "features"
        test_case = "features"
        # Define feature set to test
        features = "base,cloud,_slim"
        val_ok = "base,cloud"
        out = val_features(test_case, config, features)
        out = ','.join(sorted(out.split(',')))
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"

    if test_case == "params":
        # Define feature set to test
        features = "cloud"
        # Get JSON output
        out = val_features(test_case, config, features)
        content = json.loads(out)
        val_ok = "raw"
        out = content['convert']['format'][0]['type']
        assert out == val_ok, f"Testcase: {test_case} - Mismatch: Expected: {val_ok} <> Is: {out}"


def val_features(test_case, config, features):
    """ test features """
    # Create tmp dir
    tmp_dir = create_tmp_dir()
    prepare_parametrize_config(tmp_dir, config)
    cli_opts = f"--features {features} {test_case}"
    out = run_garden_feat(tmp_dir, cli_opts)
    return out


def prepare_parametrize_config(tmp_dir, config):
    """ Prepare given parametrize configs for further testing """
    for i in config:
        for feature_name, content in i.items():
            dname = f"{tmp_dir}/{feature_name}"
            fname = f"{dname}/info.yaml"
            # Create dir structure
            create_dir(dname) 
            # Write config files
            write_yaml(fname, content)


def create_tmp_dir():
    """ Create tmp directory """
    tmp_dir = tempfile.mkdtemp(prefix="gl-unit-test-garden-feat-")
    return tmp_dir


def create_dir(dname):
    """ Create regular directory """
    try: 
        os.mkdir(dname) 
    except OSError as error: 
        print(error) 


def write_yaml(fname, content):
    """ Write YAML files on disk """
    with open(fname, 'w') as yaml_file:
        yaml.dump(content, yaml_file, default_flow_style=True)


def run_garden_feat(tmp_dir, cli_opts):
    """ Run garden-feat binary by given cli opts """
    feat_dir = f"--featureDir {tmp_dir}"
    cmd = f"/gardenlinux/bin/garden-feat {feat_dir} {cli_opts}"
    rc, out = utils.execute_local_command(cmd)
    # Remove new lines from output
    out = out.strip()
    return out
