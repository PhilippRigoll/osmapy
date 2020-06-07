# -*- coding: utf-8 -*-

from string import Template

import requests
from PySide2 import QtCore
from PySide2.QtGui import QColor, QPen
from PySide2.QtWidgets import QMessageBox

from osmapy.ElementsLoader import Node
from osmapy.utils import calc
from osmapy.utils.config import config


class ElementsLoader:
    """ This class provides a loader for OSM elements from the OSM server.
    """

    def __init__(self):
        self.elements_copy = dict()  # copy of elements to find changes
        self.elements = dict()
        self.headers = {"Accept": "application/json", "User-Agent": config.user_agent}

        self.selected_node = None
        self.new_node_counter = -1

    def clear(self):
        """ Reset the elements dicts and the counter
        """
        self.selected_node = None
        self.new_node_counter = -1
        self.elements_copy = dict()
        self.elements = dict()

    def load(self, west, north, east, south):
        """ This function loads all node elements from a given bounding box. The function returns all nodes loaded with
        this object so far.

        Args:
            west (float): longitude of the bounding box in degree
            north (float): latitude of the bounding box in degree
            east (float): longitude of the bounding box in degree
            south (float): latitude of the bounding box in degree

        Returns:
            {Node}: dict of all OSM nodes. The keys are the IDs of the nodes.
        """
        url = config.osm_api_url + "/api/0.6/map?bbox=${west},${north},${east},${south}"
        request = Template(url)
        request = request.substitute(west=west, north=north, east=east, south=south)
        result = requests.get(request, headers=self.headers)

        if result.ok:
            result_json = result.json()
            nodes_copy = {raw["id"]: Node.Node(raw) for raw in result_json["elements"].copy() if raw["type"] == "node"}
            self.elements_copy = {**self.elements_copy, **nodes_copy}
            nodes = {raw["id"]: Node.Node(raw) for raw in result_json["elements"].copy() if raw["type"] == "node"}
            self.elements = {**self.elements, **nodes}  # merge old and new nodes
        else:
            box = QMessageBox()
            box.setWindowTitle("Error")
            box.setText("Maybe you have to zoom in because there are to many objects in this area")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()

    def new_node(self, lat, lon):
        """ Add new node to the elements list.

        Args:
            lat (float): latitude of the new node
            lon (float): longitude of the new node
        """
        self.elements[self.new_node_counter] = Node.Node.create_new_node(self.new_node_counter, lat, lon)
        self.new_node_counter -= 1

    def draw(self, viewer, qpainter, alpha):
        """ Function to draw on a View.

        Args:
            viewer (Viewer): object which must is drawn on and which must be updated
            qpainter (QPainter): object which is used to draw
            alpha (float): opacity to draw
        """
        qpainter.setOpacity(alpha)
        for elem in self.elements.values():
            qpainter.setBrush(QColor(QtCore.Qt.blue))
            qpainter.setPen(QPen(QColor(QtCore.Qt.black), 1))
            if elem.data["type"] == "node":
                x, y = calc.deg2xy(float(elem.data["lat"]), float(elem.data["lon"]))
                xscreen, yscreen = viewer.xy2screen(x, y)

                size = 6
                qpainter.drawEllipse(xscreen - size / 2, yscreen - size / 2, size, size)

                if self.selected_node and elem.id == self.selected_node:
                    qpainter.setBrush(QColor(0, 0, 0, 0))
                    qpainter.setPen(QPen(QColor(QtCore.Qt.red), 2))
                    size = 10
                    qpainter.drawRect(xscreen - size / 2, yscreen - size / 2, size, size)
