# -*- coding: utf-8 -*-
import ctypes
import os
import pathlib
import sys
from functools import partial
from subprocess import call

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QApplication, QMainWindow, QToolBar, QDockWidget)

from osmapy.Changeset.Changeset import Changeset
from osmapy.Changeset.ChangesetForm import ChangesetForm
from osmapy.ElementsLoader.ElementsLoader import ElementsLoader
from osmapy.Viewer import Viewer
from osmapy.Viewer.ElementViewer import ElementViewer
from osmapy.Viewer.LayerManager import LayerManager
from osmapy.utils import config


class Main(QMainWindow):
    """ MainWindow which contains all widgets of Osmapy.
    """

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowTitle("Osmapy")
        path_base = pathlib.Path(__file__).parent
        icon_path = str(path_base / pathlib.Path("assets/appicon.png"))
        self.setWindowIcon(QIcon(str(icon_path)))
        # All widgets should be destroyed when the main window is closed. This the widgets can use the destroyed widget
        # to allow clean up. E.g. save the database of the TileLoader.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.resize(config.config.window_size[0], config.config.window_size[1])

        self.elements_loader = ElementsLoader()

        # Element Viewer as DockWidget
        self.element_viewer = ElementViewer(self)
        self.dock_element_viewer = QDockWidget()
        self.dock_element_viewer.setWindowTitle("Element Viewer")
        self.dock_element_viewer.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dock_element_viewer.setWidget(self.element_viewer)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_element_viewer)

        # LayerManger as DockWidget
        self.layer_manager = LayerManager(self)
        self.dock_layer_manager = QDockWidget()
        self.dock_layer_manager.setWindowTitle("Layer Manager")
        self.dock_layer_manager.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dock_layer_manager.setWidget(self.layer_manager)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_layer_manager)

        self.viewer = Viewer.Viewer(self)
        self.setCentralWidget(self.viewer)
        self.viewer.setFocus()
        self.viewer.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.changeset = Changeset(self)
        self.changset_form = ChangesetForm(self)

        self.toolbar = QToolBar()
        self.toolbar.addAction("Load Elements", self.viewer.load_elements)
        self.toolbar.addAction("Undo Changes", self.viewer.undo_changes)
        self.toolbar.addAction("Create Node", partial(self.viewer.change_mode, "new_node"))
        self.toolbar.addAction("Upload Changes", self.changset_form.show)
        if os.name == "nt":
            self.toolbar.addAction("Open Configuration", partial(os.startfile, str(config.path_config)))
        elif sys.platform == "darwin":
            self.toolbar.addAction("Open Configuration", partial(call, ["open", str(config.path_config)]))
        else:
            self.toolbar.addAction("Open Configuration", partial(call, ["xdg-open", str(config.path_config)]))
        self.addToolBar(self.toolbar)

        self.statusBar().showMessage("Welcome to Osmapy!")


def main():
    # Staring point of Osmapy
    app = QApplication()
    app.setApplicationName("Osmapy")
    # show the icon in the windows taskbar
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"osmapy")
    main_window = Main()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
