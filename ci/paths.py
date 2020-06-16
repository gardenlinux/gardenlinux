import os

own_dir = os.path.abspath(os.path.dirname(__file__))
flavour_cfg_path = os.path.join(own_dir, os.pardir, 'flavours.yaml')
cicd_cfg_path = os.path.join(own_dir, 'cicd.yaml')
