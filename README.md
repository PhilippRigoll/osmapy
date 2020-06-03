# POSM - Python Editor for OpenStreetMaps

May I introduce you to __POSM__, the Python Editor for [OpenStreetMap](https://www.openstreetmap.org).
This should become the new state of the art editor for OpenStreetMap.
In contrast to the other common OSM editors this editor is based on Python.
Python is modern, has a huge user base and is battery-included.
This allows everyone to contribute to this project.
POSM uses the widespread, powerful and freshly-looking Qt-framework.

![example](examples/example.png)

![example](examples/example2.png)

Currently POSM is more like a prove of concept than a full fledged editor.
But it can already be used to modify OSM nodes.

## Features
The following Features are already implemented:
 * Interface to Slippy Tiles
    * LiFo queue to load the most needed tiles first
    * Multiple workers to download tiles
    * Caching
    * Easy configuration to chose tile servers
 * Layers
    * Multi-Layer support
    * Change layer order by Drag'n'Drop
    * Change the opacity of layers
 * GPX files
    * GPX files are easily loaded by Drag'n'Drop
 * OSM objects modification
    * Create / Modify / Delete OSM nodes
    * Add / Change / Remove Tags
    * Precise node moving with the arrow keys
    * Upload your changes to the OSM server
 * Adaptive appearance
    * All the tool windows can be moved around freely
 * Easy configuration
    * Just one YAML file must be modified
    
    
## Installation
The editor can be easily installed using pip:
```
pip install POSM
``` 

After installation run in the commandline:
```
POSM
```

The configuration file can be found here: [`POSM/config.yaml`](POSM/config.yaml)

## Small User Hints

 - Move around: Right mouse button + Mouse Move
 - Zooming: Mousewheel
 - After zooming in you can click on "Load Elements" to load the OSM elements in the visible area
 - Select Node with right click
 - Move selected Node with arrow keys
 - Remove OSM tag: click on the key of the tag
 - Drop GPX file into window to load it

# License
[GNU GPLv3](LICENSE)
 