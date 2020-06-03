# -*- coding: utf-8 -*-

from functools import partial

from PySide2.QtWidgets import QFormLayout, QWidget, QLineEdit, QLabel, QPushButton, QInputDialog


class ElementViewer(QWidget):
    """ Widget which contains a TextEdit with the information of a selected OSM element.
    """

    def __init__(self, parent):
        super(ElementViewer, self).__init__()
        self.parent = parent
        self.node = None

        self.clear()

    def clear(self):
        """ Clear ElementViewer to show no node.
        """
        QWidget().setLayout(self.layout())
        layout = QFormLayout()
        text = QLabel("Right Click to Select Node")
        text.setStyleSheet("font-weight: bold")
        layout.addRow(text)
        self.setLayout(layout)

    def set_node(self, node):
        """ Change the node shown in the ElementViewer

        Args:
            node (Node): Node that should be shown in the ElementViewer.
        """
        self.id = node.id

        QWidget().setLayout(self.layout())
        layout = QFormLayout()

        # Node information which cannot be changed by the user
        layout.addRow("Id", QLabel(str(node.id)))
        layout.addRow("Uid", QLabel(str(node.data["uid"])))
        layout.addRow("User", QLabel(str(node.data["user"])))
        layout.addRow("Version", QLabel(str(node.data["version"])))
        layout.addRow("Changeset", QLabel(str(node.data["changeset"])))
        layout.addRow("Timestamp", QLabel(str(node.data["timestamp"])))

        # Properties of nodes which can be changed by the user
        for filed_humanreadable, field in zip(["Latitiude", "Longitude"], ["lat", "lon"]):
            edit = QLineEdit(str(node.data[field]))
            layout.addRow(filed_humanreadable, edit)
            edit.textChanged.connect(partial(self.modify_property, field))

        # Tags which can be deleted an modified
        if len(node.data["tags"]) > 0:
            text = QLabel("Tags")
            text.setStyleSheet("font-weight: bold")
            layout.addRow(text)

            for key, value in node.data["tags"].items():
                key_edit = QPushButton(key)
                value_edit = QLineEdit(value)
                layout.addRow(key_edit, value_edit)
                key_edit.clicked.connect(partial(self.remove_tag, key))
                value_edit.textChanged.connect(partial(self.modify_tag, key))

        button = QPushButton("Add Tag")
        layout.addRow(button)
        button.clicked.connect(self.new_tag)

        button = QPushButton("Delete Node")
        layout.addRow(button)
        button.clicked.connect(self.delete_node)

        self.setLayout(layout)

    def delete_node(self):
        """ Delete the currently selected node.
        """
        del self.parent.elements_loader.elements[self.id]
        self.parent.elements_loader.selected_node = None
        self.parent.viewer.update()
        self.clear()

    def modify_property(self, field, value):
        """ Callback to change a nodes property by changing a text field.

        Args:
            field (str): property which should be changed
            value (str): new value
        """
        # TODO typechecking
        self.parent.elements_loader.elements[self.id].data[field] = value
        self.parent.viewer.update()

    def modify_tag(self, key, value):
        """ Callback to modify a tag

        Args:
            key (str): tag key
            value (str): tag value
        """
        self.parent.elements_loader.elements[self.id].data["tags"][key] = value
        self.parent.viewer.update()

    def remove_tag(self, key):
        """ Remove a tag from an object

        Args:
            key (str): key of the tag which should be removed
        """
        del self.parent.elements_loader.elements[self.id].data["tags"][key]
        self.set_node(self.parent.elements_loader.elements[self.id])

    def new_tag(self):
        """ Ask user for key and value of the new tag and create it.
        """
        key, ok = QInputDialog().getText(self, "New Tag", "Key", QLineEdit.Normal)
        if ok and key:
            value, ok = QInputDialog().getText(self, "New Tag", "Value", QLineEdit.Normal)
            if ok and value:
                self.parent.elements_loader.elements[self.id].data["tags"][key] = value
                self.set_node(self.parent.elements_loader.elements[self.id])
