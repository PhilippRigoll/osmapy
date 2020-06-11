# -*- coding: utf-8 -*-

import json
import multiprocessing
import pathlib
import queue
import random
import threading
import time
from io import BytesIO
from string import Template

import numpy as np
import requests
from PIL import Image
from PySide2.QtGui import QPixmap

from osmapy.TileLoader.Tile import Tile
from osmapy.utils.config import config


class TileLoader:
    """ Class to load slippy tiles in a LIFO queue with workers. The tiles are cached and a cache database with a dict
    is maintained. The Tile Usage Policy of OSM is followed https://operations.osmfoundation.org/policies/tiles/.
    """

    def __init__(self, viewer, config_id):
        """ The constructor needs a viewer reference to update the map as soon as the slippy tile is loaded.

        Args:
            viewer (Viewer): viewer object where the slippy tile should be shown
        """
        self.name = config.slippy_tiles[config_id].name
        self.urls = config.slippy_tiles[config_id].urls

        self.path_cache = pathlib.Path(__file__).parent / pathlib.Path(f"../../cache/{self.name}")
        self.viewer = viewer

        self.cache_json = self.load_cache_json()

        self.queue = queue.LifoQueue()
        self.lock = multiprocessing.Lock()

        for _ in range(min(2, multiprocessing.cpu_count())):    # only two download threads are allowed
            threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        """ Worker which downloads the tile, updates the cache database and saves the image. After this processed is
        finished the viewer which requested the image is updated.
        """
        while True:
            tile = self.queue.get()
            # If an error occurse during the loading process the worker should't be blocked. The loading process is
            # tried again later, because the status of the tile in the cache database is still 'loading'.
            try:
                osm_tile_url = random.choice(self.urls)  # randomly chose one of the servers in the list
                request = Template(osm_tile_url)
                request = request.substitute(zoom=tile.zoom, int_xtile=tile.int_xtile, int_ytile=tile.int_ytile)
                # According to the OSM Tile Usage Policy an User-Agent is set
                headers = {"User-Agent": config.user_agent}
                response = requests.get(request, headers=headers)
                image = Image.open(BytesIO(response.content))

                with self.lock:     # to make the database thread safe
                    image.save(self.path_cache / f"{tile.name}.png")    # TODO can images corrupt when window is closed?
                    expire_time = 60 * 60 * 24 * 7  # 7 days
                    self.cache_json[tile.name]["time"] = time.time() + expire_time
                    self.cache_json[tile.name]["state"] = "loaded"
                    self.viewer.update()

                self.queue.task_done()
            except Exception as e:
                # an error needn't been handled any further because the loading will be retried automatically
                print("Error:", e)

    def get_tile(self, tile):
        """ Request a tile to be loaded.

        Args:
            tile (Tile): tile object of the tile which should be loaded.

        Returns:
            str: path where the slippy tile will be saved after loading from a worker. Returns None if the tile cannot
            exist.
        """
        if not tile.check_existance():
            return None

        with self.lock:
            if tile.name not in self.cache_json:    # load tile if it is not already in the cache database
                # set set state of the tile to loading and save the current time to allow loading retries after a
                # given time
                self.cache_json[tile.name] = {"state": "loading",
                                              "time": time.time()}
                self.queue.put(tile)
            if tile.name in self.cache_json:
                # if the tile is already in the cache database and the loading is not yet finished but a waiting time
                # is exceeded. The loading will be tried again.
                if self.cache_json[tile.name]["state"] == "loading" and \
                        self.cache_json[tile.name]["time"] + config.retry_time_tile < time.time():
                    self.cache_json["time"] = time.time()
                    self.queue.put(tile)
                # reload after reaching expiring date
                if self.cache_json[tile.name]["state"] == "loaded" and \
                        self.cache_json[tile.name]["time"] < time.time():
                    self.cache_json[tile.name] = {"state": "loading",
                                                  "time": time.time()}
                    self.queue.put(tile)

        return str(self.path_cache / f"{tile.name}.png")

    def load_cache_json(self):
        """ Load the cache database which is a json file. If the database does not exists create it with its folder.

        Returns:
            (dict): the cache database as a dict
        """
        path = self.path_cache / "database.json"
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as json_file:
                json.dump(dict(), json_file)
        with open(path, "r") as json_file:
            return json.load(json_file)

    def save_cache_json(self):
        """ Save cache database back to a file.
        """
        path = self.path_cache / "database.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as json_file:
            json.dump(self.cache_json, json_file)

    def close(self):
        """ This is triggered when the parent of the object is destroyed. So this should fire if the main window is
        closed and the database will be saved to a file when no worker changes the database.
        """
        # TODO is there a better/safer way?
        with self.lock:
            self.save_cache_json()

    def draw(self, viewer, qpainter, alpha):
        """ Function to draw on a View.

        Args:
            viewer (Viewer): object which must is drawn on and which must be updated
            qpainter (QPainter): object which is used to draw
            alpha (float): opacity to draw
        """
        qpainter.setOpacity(alpha)
        main_tile = Tile(viewer.lat, viewer.lon, viewer.zoom)
        offset_x = int((viewer.x - main_tile.center_x) * viewer.scale_x)
        offset_y = int((viewer.y - main_tile.center_y) * viewer.scale_y)
        num_x = int(np.ceil(int(np.ceil(viewer.frameGeometry().width() / config.image_size) + 1) / 2))
        num_y = int(np.ceil(int(np.ceil(viewer.frameGeometry().height() / config.image_size) + 1) / 2))

        for a in range(-num_x, num_x + 1):
            for b in range(-num_y, num_y + 1):
                tile = Tile.from_num(main_tile.xtile + a, main_tile.ytile + b, main_tile.zoom)
                if not tile.check_existance():
                    continue
                path_image = self.get_tile(tile)

                # try:
                if pathlib.Path(path_image).is_file():
                    pic = QPixmap(str(path_image))
                else:
                    pic = QPixmap(viewer.asset_error_image)

                pic = pic.scaled(config.image_size, config.image_size)
                qpainter.drawTiledPixmap(
                    -offset_x + a * config.image_size + viewer.frameGeometry().width() * 0.5 - config.image_size * 0.5,
                    offset_y + b * config.image_size + viewer.frameGeometry().height() * 0.5 - config.image_size * 0.5,
                    config.image_size, config.image_size, pic)
