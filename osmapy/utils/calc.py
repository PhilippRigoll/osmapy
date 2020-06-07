# -*- coding: utf-8 -*-

""" In this file all the necessary calculations should be defined.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class Bbox_deg:
    """ Class for a bounding box.
    """
    left: float
    top: float
    right: float
    bottom: float


@dataclass
class Bbox_xy:
    """ Class for a bounding box.
    """
    left: float
    top: float
    right: float
    bottom: float


def xy2deg(x, y):
    """ Calculate the latitude and longitude in degree given the mercator x and y.

    Args:
        x (float): mercator x
        y (float): mercator y

    Returns:
        (float, float): tuple with the latitude and longitude in degree
    """
    return (180.0 / np.pi * (2.0 * np.arctan(np.exp(y * np.pi / 180.0)) - np.pi / 2.0), x)


def deg2xy(lat, lon):
    """ Calculate the mercator x and y given the longitude and latitiude in degree.

    Args:
        lat (float): latitude in degree
        lon (float): longitude in degree

    Returns:
        (float, float): tuple with the mercator x and y
    """
    return (lon, 180.0 / np.pi * np.log(np.tan(np.pi / 4.0 + lat * (np.pi / 180.0) / 2.0)))


def deg2num(lat, lon, zoom):
    """ Calculate the slippy tile numbers given a latitude and longitude in degree and the zoom level.

    Args:
        lat (float): latitude in degree
        lon (float): longitude in degree
        zoom (int): zoom level of the tile

    Returns:
        (float, float): tuple with the x and y of the tile. Must be converted to integer to use it with a tile
                        server
    """
    lat_rad = np.radians(lat)
    n = 2.0 ** zoom
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    """ Calculate the latitude and longitude in degree given the slippy tile numbers.

    Args:
        xtile (float): x of the tile
        ytile (float): y of the tile
        zoom (int): zoom level of the tile

    Returns:
        (float, float): tuple with the latitude and longitude in degree
    """
    n = 2.0 ** zoom
    lon = xtile / n * 360.0 - 180.0
    lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * ytile / n)))
    lat = np.degrees(lat_rad)
    return (lat, lon)


def get_bbox_deg(xtile, ytile, zoom):
    """ Calculate bounding box of a tile.

    Args:
        xtile (float): x of the tile
        ytile (float): y of the tile
        zoom (int): zoom level of the tile

    Returns:
        (Bbox): dataclass with the bounding box
    """
    top, left = num2deg(xtile, ytile, zoom)
    bottom, right = num2deg(xtile + 1, ytile + 1, zoom)
    bbox = Bbox_xy(left=left, top=top, right=right, bottom=bottom)
    return bbox


def get_bbox_xy(xtile, ytile, zoom):
    """ Calculate bounding box of a tile.

    Args:
        xtile (float): x of the tile
        ytile (float): y of the tile
        zoom (int): zoom level of the tile

    Returns:
        (Bbox): dataclass with the bounding box
    """
    top, left = deg2xy(*num2deg(xtile, ytile, zoom))
    bottom, right = deg2xy(*num2deg(xtile + 1, ytile + 1, zoom))
    bbox = Bbox_xy(left=left, top=top, right=right, bottom=bottom)
    return bbox
