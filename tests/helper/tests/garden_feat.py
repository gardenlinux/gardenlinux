import os
import yaml
import json
import tempfile
from helper import utils


def garden_feat(test_case, config, input_features, output_features):
    """Check the MD5 sums of installed Debian packages"""

    # Run tests for all garden-feat cli opts
    out = val_features(test_case, config, input_features)

    # Prepare output
    if test_case == "params":
        # Get JSON output
        content = json.loads(out)
        out = content['convert']['format'][0]['type']
    else:
        out = val_features(test_case, config, input_features)
        out = ','.join(out.split(','))

    assert out == output_features, f"Testcase: {test_case} - Mismatch: Expected: {output_features} <> Is: {out}"


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
