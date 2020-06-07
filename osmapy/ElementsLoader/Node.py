# -*- coding: utf-8 -*-

import lxml.etree as ET

from osmapy.utils import calc


class Node:
    """ Class to represent an OSM node.
    """

    def __init__(self, raw):
        """ The constructer uses the raw dictionary of the OSM server answer.

        Args:
            raw (dict): OSM server result for this object.
        """
        self.raw = raw.copy()
        self.id = self.raw["id"]

        self.data = dict(id=str(self.raw["id"]),
                         uid=str(self.raw["uid"]),
                         user=str(self.raw["user"]),
                         version=str(self.raw["version"]),
                         changeset=str(self.raw["changeset"]),
                         timestamp=str(self.raw["timestamp"]),
                         type="node",
                         lat=str(self.raw["lat"]),
                         lon=str(self.raw["lon"]))

        if "tags" in self.raw:
            self.data["tags"] = self.raw["tags"].copy()
        else:
            self.data["tags"] = dict()

        self.x, self.y = calc.deg2xy(self.raw["lat"], self.raw["lon"])
        self.trigger = False

    @classmethod
    def create_new_node(cls, id, lat, lon):
        """ Create a new node and add it to the elements list

        Args:
            id (int): id of the new element
            lat (float): latitude of the new node
            lon (float): longitude of the new node

        Returns:
            Node: new node object
        """
        new_raw = dict(id=id,
                       uid="-1",
                       user="-1",
                       version="0",
                       changeset="-1",
                       timestamp="-1",
                       type="node",
                       lat=lat,
                       lon=lon,
                       tags=dict())
        return cls(new_raw)

    def create_xml(self, id, changeset=None, tags=True):
        """ Create XML representation of the node. Can be used to create a osmChange file.

        Args:
            id (int): id which should be shown in the XML
            tags (bool): the tags should be omitted when deleting a node
        """
        if not changeset:
            changeset = self.data["changeset"]

        xml_node = ET.Element("node",
                              id=str(id),
                              changeset=str(changeset),
                              version=str(self.data["version"]),
                              lat=str(self.data["lat"]),
                              lon=str(self.data["lon"]))

        if tags:
            for key, value in self.data["tags"].items():
                ET.SubElement(xml_node, "tag", k=key, v=value)

        return xml_node

    def set_position(self, x, y):
        """ Set new position of node

        Args:
            x (float): mercator x
            y (float): mercator y
        """
        self.x = x
        self.y = y
        lat, lon = calc.xy2deg(x, y)
        self.data["lat"], self.data["lon"] = str(lat), str(lon)

    def __str__(self):
        """ XML representation of the node.

        Returns:
            str: XML representation as a string
        """
        return ET.tostring(self.create_xml(self.id)).decode()

    def __eq__(self, other):
        """ Compare two node objects, by their string XML representation.

        Args:
            other (Node): node to compare

        Returns:
            bool
        """
        return ET.tostring(self.create_xml(1)).decode() == ET.tostring(other.create_xml(1)).decode()

    def __ne__(self, other):
        """ Compare two node objects, by their string XML representation.

        Args:
            other (Node): node to compare

        Returns:
            bool
        """
        return not self.__eq__(other)
