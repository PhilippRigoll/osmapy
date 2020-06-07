# -*- coding: utf-8 -*-

import lxml.etree as ET
import requests

from osmapy.utils.config import config


class Changeset:
    """ Represent a changeset. Create it and send it to the server.
    """

    def __init__(self, parent):
        self.parent = parent
        self.osm_api_url = config.osm_api_url

        self.headers = {"User-Agent": config.user_agent, "Content-Type": "application/xml"}

    def submit(self, comment, username, password):
        """ Submit the changeset to the server.

        Args:
            comment (str): comment of this changeset
            username (str): users username
            password (str): users password
        """
        self.username = username
        self.password = password

        status_code = self.create_changeset(comment)
        if status_code != 200:
            return status_code

        osmChange = ET.tostring(self.create_osmChange(self.changeset_id))
        status_code = self.upload_diff(osmChange)
        if status_code != 200:
            return status_code

        status_code = self.close()
        if status_code != 200:
            return status_code

        self.parent.element_viewer.clear()
        self.parent.elements_loader.clear()
        self.parent.viewer.update()

        return status_code

    def create_changeset(self, comment):
        """ Ask server to create a changeset.

        Args:
            comment (str): comment for this changeset

        Returns:
            http status code of the response
        """
        root = ET.Element("osm")
        changeset = ET.SubElement(root, "changeset")
        ET.SubElement(changeset, "tag", k="comment", v=comment)
        tree = ET.ElementTree(root)

        request = f"{config.osm_api_url}/api/0.6/changeset/create"
        result = requests.put(request, data=ET.tostring(tree), headers=self.headers,
                              auth=(self.username, self.password))
        if result.status_code == 200:
            self.changeset_id = int(result.text)
        return result.status_code

    def create_osmChange(self, changeset_id):
        """ Create a osmChange XML file which describes the changes which where perfromed by the user.

        Args:
            changeset_id (int): number of the changeset declared by the server

        Returns:
            xml tree: containing all changes as an xml
        """
        elements_copy = self.parent.elements_loader.elements_copy
        elements = self.parent.elements_loader.elements

        root = ET.Element("osmChange")

        # created
        create = ET.SubElement(root, "create")

        created_node_keys = set(elements) - set(elements_copy)
        created_nodes = [elements[k] for k in created_node_keys]

        for i, node in enumerate(created_nodes):
            create.insert(-1, node.create_xml(-i - 1, changeset_id))

        # deleted
        delete = ET.SubElement(root, "delete")

        deleted_node_keys = set(elements_copy) - set(elements)
        deleted_nodes = [elements_copy[k] for k in deleted_node_keys]

        for i, node in enumerate(deleted_nodes):
            delete.insert(-1, node.create_xml(node.id, changeset_id, tags=False))

        # modified
        modify = ET.SubElement(root, "modify")

        keys = set(elements).intersection(set(elements_copy))
        modified_nodes = [elements[k] for k in keys if elements[k] != elements_copy[k]]

        for i, node in enumerate(modified_nodes):
            modify.insert(-1, node.create_xml(node.id, changeset_id))

        tree = ET.ElementTree(root)

        return tree

    def upload_diff(self, osm_change):
        """ Upload osmChange file to the server

        Args:
            osm_change (str): xml as a string

        Returns:
            http status code of the response
        """
        request = f"{config.osm_api_url}/api/0.6/changeset/{self.changeset_id}/upload"
        result = requests.post(request, data=osm_change, headers=self.headers, auth=(self.username, self.password))
        return result.status_code

    def close(self):
        """ Close the changeset to finish the editing

        Returns:
            http status code of the response
        """
        request = f"{config.osm_api_url}/api/0.6/changeset/{self.changeset_id}/close"
        result = requests.put(request, headers=self.headers, auth=(self.username, self.password))
        return result.status_code
