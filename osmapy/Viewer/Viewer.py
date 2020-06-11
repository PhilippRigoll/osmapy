# -*- coding: utf-8 -*-

import pathlib
import webbrowser

import numpy as np
from PySide2 import QtCore
from PySide2.QtGui import QPainter, QColor, QPen
from PySide2.QtWidgets import (QDialog, QApplication)

from osmapy.GPXLoader.GPXLoader import GPXLoader
from osmapy.TileLoader import TileLoader, Tile
from osmapy.Viewer.OSMCopyright import OSMCopyright
from osmapy.utils import calc
from osmapy.utils.config import config


class Viewer(QDialog):
    """ Viewer widget where the map is shown with the slippy tiles in the background and OSM objects.
    """

    def __init__(self, parent=None):
        super(Viewer, self).__init__()

        self.tile_loaders = []
        for config_id in range(len(config.slippy_tiles)):
            self.tile_loaders.append(TileLoader.TileLoader(self, config_id))
        self.parent = parent
        self.element_viewer = self.parent.element_viewer

        self.lat = config.start_latitude
        self.lon = config.start_longitude
        self.zoom = config.start_zoom
        self.x, self.y = calc.deg2xy(self.lat, self.lon)

        # scale
        tile = Tile.Tile(self.lat, self.lon, self.zoom)
        self.scale_x = config.image_size / tile.width_x
        self.scale_y = config.image_size / tile.width_y

        self.click = False

        self.elements_loader = self.parent.elements_loader

        for tile_loader in self.tile_loaders:
            self.destroyed.connect(tile_loader.close)

        path_base = pathlib.Path(__file__).parent
        self.asset_error_image = str(path_base / pathlib.Path("../assets/error.png"))

        self.osm_copyright = OSMCopyright()

        self.setAcceptDrops(True)  # allow file dropping

        self.layers = self.parent.layer_manager
        for config_id, tile_loader in enumerate(self.tile_loaders):
            self.layers.add_layer(tile_loader, config.slippy_tiles[config_id].name, config.slippy_tiles[config_id].enabled)
        self.layers.add_layer(self.elements_loader, "OSM Nodes")

        self.mode = "normal"  # mode for clicking events

    def set_deg(self, lat, lon):
        """ Set center of the view.

        Args:
            lat (float): latitude of the center
            lon (float): longitude of the center
        """
        self.lat = lat
        self.lon = lon
        self.x, self.y = calc.deg2xy(self.lat, self.lon)
        self.set_zoom(self.zoom)

    def set_xy(self, x, y):
        """ Set center of the view.

        Args:
            x (float): mercator x of the center
            y (float): mercator y of the center
        """
        self.x = x
        self.y = y
        self.lat, self.lon = calc.xy2deg(self.x, self.y)
        self.set_zoom(self.zoom)

    def set_zoom(self, zoom):
        """ Set zoom level of the view.

        Args:
            zoom (int): zoom level
        """
        self.zoom = zoom
        self.parent.statusBar().showMessage(f"Lat: {self.lat:.7f} Lon: {self.lon:.7f} Zoom: {zoom}")
        tile = Tile.Tile(self.lat, self.lon, self.zoom)
        self.scale_x = config.image_size / tile.width_x
        self.scale_y = config.image_size / tile.width_y

    def screen2xy(self, xscreen, yscreen):
        """ Convert from screen coordinates to mercator coordinates.

        Args:
            xscreen (float): x coordinate on view
            yscreen (float): y coordinate on view

        Returns:
            (float, float): mercator x and y
        """
        xscreen -= self.frameGeometry().width() / 2
        yscreen -= self.frameGeometry().height() / 2
        yscreen *= -1
        xscreen /= self.scale_x
        yscreen /= self.scale_y

        xscreen += self.x
        yscreen += self.y

        return xscreen, yscreen

    def xy2screen(self, x, y):
        """ Convert mercator x and y to screen coordinates.

        Args:
            x (float): mercator x
            y (float): mercator y

        Returns:
            (float, float): coordinates on the view
        """
        xscreen = (x - self.x) * self.scale_x + self.frameGeometry().width() / 2
        yscreen = -(y - self.y) * self.scale_y + self.frameGeometry().height() / 2
        return xscreen, yscreen

    def paintEvent(self, event):
        """ This is triggered on every update. All the connected layers are drawn here. Also the copyright information
        is added here.

        Args:
            event (Event): not yet used
        """
        qpainter = QPainter(self)
        qpainter.setRenderHint(QPainter.Antialiasing)

        for layer, alpha in self.layers.get_layers():
            layer.draw(self, qpainter, alpha)

        qpainter.setBrush(QColor(0, 0, 0, 0))
        qpainter.setPen(QPen(QColor(QtCore.Qt.black), 1))
        size = 4
        qpainter.drawRect(- size / 2 + self.frameGeometry().width() * 0.5,
                          - size / 2 + self.frameGeometry().height() * 0.5, size, size)

        # draw OSM information
        self.osm_copyright.draw(self, qpainter)

    def wheelEvent(self, event):
        """ Callback when the mouse wheel is used. Here the zooming is realized.

        Args:
            event (Event): scrolling event includes the amount of scrolling
        """
        if abs(event.delta()) != 0:
            delta = event.delta() // abs(event.delta())
            if delta == 1 and self.zoom < 19:
                self.set_zoom(self.zoom + 1)

                self.update()
            if delta == -1 and self.zoom > 0:
                self.set_zoom(self.zoom - 1)
                self.update()

    def mouseMoveEvent(self, event):
        """ Callback when the mouse is moved. Here the dragging of the map is realized.

        Args:
            event (Event): contains the position of the mouse
        """
        if event.buttons() == QtCore.Qt.LeftButton:
            if not self.click:
                self.start = event.globalPos()
                self.click = True
                self.start_x = self.x
                self.start_y = self.y
            else:
                moved = event.globalPos() - self.start
                set_x=self.start_x - moved.x() / self.scale_x
                set_y=self.start_y + moved.y() / self.scale_y

                set_x = np.clip(set_x, -179.999999, 179.999999) #TODO Prevent map from disappearing when x or y = 180 or -180
                set_y = np.clip(set_y, -179.999999, 179.999999)

                self.set_xy(set_x, set_y)
                self.update()

    def mouseReleaseEvent(self, event):
        """ Callback when the mouse is released. This is needed to realize the dragging.

        Args:
            event (Event): not yet used
        """
        self.click = False

    def mousePressEvent(self, event):
        """ Callback when the mouse is clicked. This is use to react on a click on the OSM copyright, select a node
        or create a new node.

        Args:
            event (Event): contains the click information
        """
        if event.buttons() == QtCore.Qt.LeftButton:
            # click on copyright
            if event.x() > self.frameGeometry().width() - self.osm_copyright.width - self.osm_copyright.margin and \
                    event.y() > self.frameGeometry().height() - self.osm_copyright.height - self.osm_copyright.margin:
                webbrowser.open(self.osm_copyright.url)
                return

        if self.mode == "normal":
            if event.buttons() == QtCore.Qt.RightButton:
                posx = event.x()
                posy = event.y()
                smallest = 9999999
                elem_id = None
                for key, elem in self.elements_loader.elements.items():
                    xscreen, yscreen = self.xy2screen(elem.x, elem.y)
                    dist = np.sqrt((xscreen - posx) ** 2 + (yscreen - posy) ** 2)
                    if dist < smallest:
                        elem_id = key
                        smallest = dist
                if elem_id:
                    self.elements_loader.selected_node = elem_id
                    self.update()
                    self.element_viewer.set_node(self.elements_loader.elements[elem_id])
        elif self.mode == "new_node":
            if event.buttons() == QtCore.Qt.RightButton:
                x, y = self.screen2xy(event.x(), event.y())
                lat, lon = calc.xy2deg(x, y)
                self.elements_loader.new_node(lat, lon)
                self.update()
                self.change_mode("normal")

    def dragEnterEvent(self, event):
        """ This callback is fired when something is dragged above the view. It is shown to the user that this is
        accepted to allow dropping GPX files.

        Args:
            event (Event): information of the dragged object
        """

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """ Event when something is dropped into the view. This is used to read GPX files.

        Args:
            event (Event): includes the dropping metadata
        """
        path = pathlib.Path(event.mimeData().urls()[0].toLocalFile())
        self.layers.add_layer(GPXLoader(path), event.mimeData().urls()[0].toLocalFile())

        self.update()

    def keyPressEvent(self, event):
        """ Callback for keypress events. This is used to move the selected object around. this scales with the zoom
        level.

        Args:
            event (Event): contains the information of the pressed key
        """
        if self.parent.elements_loader.selected_node:
            node_id = self.parent.elements_loader.selected_node
            node = self.parent.elements_loader.elements[node_id]
            if event.key() == QtCore.Qt.Key_Right:
                node.set_position(node.x + 1 / self.scale_x, node.y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()
            if event.key() == QtCore.Qt.Key_Left:
                node.set_position(node.x - 1 / self.scale_x, node.y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()
            if event.key() == QtCore.Qt.Key_Up:
                node.set_position(node.x, node.y + 1 / self.scale_y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()
            if event.key() == QtCore.Qt.Key_Down:
                node.set_position(node.x, node.y - 1 / self.scale_y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()

    def load_elements(self):
        """ Start loading OSM elements from the api which belong in the current map view.
        """
        left, top = self.screen2xy(0, 0)
        right, bottom = self.screen2xy(self.frameGeometry().width(), self.frameGeometry().height())
        north, west = calc.xy2deg(left, bottom)
        south, east = calc.xy2deg(right, top)
        self.elements_loader.load(west, north, east, south)

        self.update()

    def undo_changes(self):
        """ Undo the changes of the nodes.
        """
        self.parent.element_viewer.clear()
        self.parent.elements_loader.clear()
        self.update()
        self.load_elements()

    def change_mode(self, mode):
        """ Changes what happens when the mouse is clicked in the view. Also changes the cursor style.

        Args:
            mode (str): humanreadable mode code
        """
        self.parent.setToolTip("")
        if mode == "new_node":
            self.parent.setToolTip("Right Click to create Node")
            QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        if mode == "normal":
            QApplication.restoreOverrideCursor()
        self.mode = mode
