import os

own_dir = os.path.abspath(os.path.dirname(__file__))
repo_root = os.path.abspath(os.path.join(own_dir, os.pardir))

cicd_cfg_path = os.path.join(own_dir, 'cicd.yaml')
package_alias_path = os.path.join(own_dir, 'package_aliases.yaml')

flavour_cfg_path = os.path.join(repo_root, 'flavours.yaml')
version_path = os.path.join(repo_root, 'VERSION')
