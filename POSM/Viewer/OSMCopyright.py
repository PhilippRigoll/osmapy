# -*- coding: utf-8 -*-

from PySide2.QtCore import QRect
from PySide2.QtGui import QBrush, QColor, QStaticText


class OSMCopyright:
    """ Class for the OSM copy right in the right bottom corner of the map.
    """

    def __init__(self):
        self.width, self.height = 152, 15
        self.margin = 2
        self.url = "https://www.openstreetmap.org/copyright"

        self.copyright_text = QStaticText("© OpenStreetMap contributors")

    def draw(self, viewer, qpainter):
        """ Function to draw on a View.

        Args:
            viewer (Viewer): object which must is drawn on and which must be updated
            qpainter (QPainter): object which is used to draw
        """
        self.rect = QRect(viewer.frameGeometry().width() - self.width - self.margin,
                          viewer.frameGeometry().height() - self.height - self.margin,
                          self.width + self.margin,
                          self.height + self.margin)
        qpainter.fillRect(self.rect, QBrush(QColor(255, 255, 255)))
        qpainter.drawStaticText(viewer.frameGeometry().width() - self.width,
                                viewer.frameGeometry().height() - self.height,
                                self.copyright_text)
