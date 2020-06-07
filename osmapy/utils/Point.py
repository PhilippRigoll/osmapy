# -*- coding: utf-8 -*-

import numpy as np

from osmapy.utils import calc


class Point:
    """ Class to manage a point on the earth. Uses latitude, longitude and the meracator coordinates.
    """

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.x, self.y = calc.deg2xy(lat, lon)

    @classmethod
    def from_deg(cls, lat, lon):
        return cls(lat, lon)

    @classmethod
    def from_xy(cls, x, y):
        lat, lon = calc.xy2deg(x, y)
        return cls(lat, lon)

    def __repr__(self):
        return f"Lat: {self.lat} Lon: {self.lon}"

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point.from_xy(x, y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point.from_xy(x, y)

    def __abs__(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)
