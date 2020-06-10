# -*- coding: utf-8 -*-


class Way:
    """ Class to represent an OSM way.
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
                         type="ways",
                         nodes=self.raw["nodes"])
