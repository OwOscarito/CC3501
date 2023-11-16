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
# ^
# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import grafica.transformations as tr
import utils.shapes as shapes
from utils.camera import OrbitCamera
from utils.scene_graph import SceneGraph
from utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path
from Box2D import b2PolygonShape, b2World

from scenes.hangar import Hangar
from scenes.circuit import Circuit

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.keys_state = {}
        self.program_state = {
            "total_time": 0.0,
            "camera": None,
            "bodies": {},
            "world": None,
            # parámetros para el integrador
            "vel_iters": 6,
            "pos_iters": 2 }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.keys_state.get(key, False)

    def on_key_press(self, symbol, modifiers):
        controller.keys_state[symbol] = True
        super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        controller.keys_state[symbol] = False

class SceneController():
    def __init__(self, controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline):
        self.scene = Hangar(controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline)
        self.textured_mesh_lit_pipeline = textured_mesh_lit_pipeline
        self.color_mesh_lit_pipeline = color_mesh_lit_pipeline

    def update(self, dt):
        self.scene.update(dt)

    def draw(self):
        self.scene.draw()

    def nextScene(self):
        nextScene = self.scene.nextScene()
        self.scene = nextScene

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.nextScene()
        self.scene.on_key_press(symbol, modifiers)


if __name__ == "__main__":
    # Preparar Controller
    controller = Controller("Tarea 3", width=WIDTH, height=HEIGHT, resizable=True)

    # Preparar Pipelines 
    color_mesh_lit_pipeline = init_pipeline(
        get_path("shaders/color_mesh_lit.vert"),
        get_path("shaders/color_mesh_lit.frag"))

    textured_mesh_lit_pipeline = init_pipeline(
        get_path("shaders/textured_mesh_lit.vert"),
        get_path("shaders/textured_mesh_lit.frag"))

    # Instancia de la cámara
    controller.program_state["camera"] = OrbitCamera(5.5, "perspective")
    controller.program_state["camera"].phi = np.pi / 4
    controller.program_state["camera"].theta = 3*(np.pi) / 8

    # Cargamos la escena
    axis_scene = init_axis(controller)
    sceneController = SceneController(controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline)

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)
        
    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        axis_scene.draw()
        sceneController.draw()
    
    @controller.event
    # Cambiar autos en ciclo
    def on_key_press(symbol, modifiers):
        sceneController.on_key_press(symbol, modifiers)

    @controller.event
    def update(dt):
        controller.program_state["total_time"] += dt
        sceneController.update(dt)
        camera = controller.program_state["camera"]
        camera.update()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    