# -*- coding: utf-8 -*-

import numpy as np

from osmapy.utils import calc
from osmapy.utils.config import config


class Tile:
    """ Class to represent a slippy tile.
    """

    def __init__(self, lat, lon, zoom):
        """ Constructer with the latitude and longitude which should lay inside of the slippy tile.

        Args:
            lat (float): latitude of a position which should lay inside of the tile
            lon (float): longitude of a position which should lay inside of the tile
            zoom (int): zoom level of the tile
        """
        self.lat = lat
        self.lon = lon
        self.zoom = zoom

        self.x, self.y = calc.deg2xy(self.lat, self.lon)

        self.xtile, self.ytile = calc.deg2num(self.lat, self.lon, self.zoom)

        self.int_xtile, self.int_ytile = int(self.xtile), int(self.ytile)

        self.bbox_deg = calc.get_bbox_deg(self.xtile, self.ytile, self.zoom)
        self.bbox_xy = calc.get_bbox_xy(self.xtile, self.ytile, self.zoom)

        self.width_x = np.abs(self.bbox_xy.left - self.bbox_xy.right)
        self.width_y = np.abs(self.bbox_xy.top - self.bbox_xy.bottom)

        self.center_x, self.center_y = calc.deg2xy(*calc.num2deg(self.int_xtile + 0.5, self.int_ytile + 0.5, self.zoom))

        self.scale_x = np.abs(self.bbox_xy.left - self.bbox_xy.right) / config.image_size
        self.scale_y = np.abs(self.bbox_xy.top - self.bbox_xy.left) / config.image_size

        self.name = f"{self.int_xtile}_{self.int_ytile}_{self.zoom}"  # internal name of this tile

    @classmethod
    def from_num(cls, xtile, ytile, zoom):
        """ Alternative constructor using the slippy tile numbers.

        Args:
            xtile (float): x slippy tile number of the requested tile
            ytile (float): y slippy tile number of the requested tile
            zoom (int): zoom level of the tile
        """
        lat, lon = calc.num2deg(xtile, ytile, zoom)
        return cls(lat, lon, zoom)

    def check_existance(self):
        """ Checks if the tilenumbers are valid and if the tile can exists on a slippy tile server.

        Returns:
            bool: True if tile can exists, False if not
        """
        # these bounds are given by the mercator projection
        if 0 <= self.xtile <= 2**self.zoom and 0 <= self.ytile <= 2**self.zoom:
            return True
        return False
