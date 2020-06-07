# -*- coding: utf-8 -*-

""" A yaml configuration file is loaded and converted to a dict which allows the use of the dot operator. Some
configurations are hardcoded here.
"""

import pathlib

import yaml
from easydict import EasyDict

path_base = pathlib.Path(__file__).parent
path_config = path_base / pathlib.Path("../config.txt")

with open(path_config, "r") as file:
    config = EasyDict(yaml.safe_load(file))

config.image_size = 256     # tile size
config.retry_time_tile = 4  # Wait 4 seconds before retry to load a slippy tile
