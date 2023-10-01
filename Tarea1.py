import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
from pathlib import Path

# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
import grafica.transformations as tr
import utils.shapes as shapes

WIDTH = 640
HEIGHT = 640