# -*- coding: utf-8 -*-

""" A yaml configuration file is loaded and converted to a dict which allows the use of the dot operator. Some
configurations are hardcoded here.
"""

import json
import pathlib
import re
import sys

import yaml
from PySide2.QtWidgets import QMessageBox, QApplication
from cerberus import Validator
from easydict import EasyDict

from osmapy.utils.config_schema import schema

path_base = pathlib.Path(__file__).parent
path_config = path_base / pathlib.Path("../config.txt")

with open(path_config, "r") as file:
    v = Validator(schema)
    try:
        doc = yaml.safe_load(file)
        if not v.validate(doc, schema):
            app = QApplication()
            box = QMessageBox()
            box.setWindowTitle("Configuration Error")
            errdump = json.dumps(v.errors, sort_keys=True, indent=3)
            errdump = re.sub('( *{\n)|(\s*\[)|(\s*\]\s*)|(\s*\})|(})|"', "", errdump)
            box.setText(f"There are errors in your configuration file.\n\n"
                        f"{errdump}\n\n"
                        f"The path of the configuration file should be:\n"
                        f"{path_config.resolve()}")
            box.setIcon(QMessageBox.Icon.Warning)
            box.show()
            sys.exit(app.exec_())
    except SystemExit:
        exit()
    except:
        app = QApplication()
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setText(f"Something went wrong while loading your config file.\n"
                    f"The path of the configuration file should be:\n"
                    f"{path_config.resolve()}")
        box.setIcon(QMessageBox.Icon.Warning)
        box.show()
        sys.exit(app.exec_())

    config = EasyDict(doc)

config.image_size = 256  # tile size
config.retry_time_tile = 4  # Wait 4 seconds before retry to load a slippy tile
