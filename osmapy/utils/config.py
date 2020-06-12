# -*- coding: utf-8 -*-

""" A yaml configuration file is loaded and converted to a dict which allows the use of the dot operator. Some
configurations are hardcoded here.
"""

import pathlib
import yaml

from easydict import EasyDict
from cerberus import Validator

path_base = pathlib.Path(__file__).parent
path_config = path_base / pathlib.Path("../config.txt")
path_schema = path_base / pathlib.Path("schema.py")



with  open(path_config, "r") as file:
    schema = eval(open(path_schema, 'r').read())
    v = Validator(schema)
    try:
        doc = yaml.safe_load(file)
    except:
        print("Something went wrong while loading your config file. Please check it for format errors.")
        exit()

    if not v.validate(doc, schema):
        print("There are errors in your configuration file.")
        print (v.errors)
        exit()

    config = EasyDict(doc)
         

config.image_size = 256     # tile size
config.retry_time_tile = 4  # Wait 4 seconds before retry to load a slippy tile
