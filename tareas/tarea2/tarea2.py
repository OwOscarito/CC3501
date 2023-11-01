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
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = { "total_time": 0.0, "camera": None }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]

def make_hangar(graph):
    graph.add_node("hangar",
                    attach_to="root", 
                    position=[0, -1, 0]
                )
    graph.add_node("floor",
                    attach_to="hangar",
                    mesh=square,
                    texture = concrete_texture,
                    material = concrete_material,
                    pipeline = textured_mesh_lit_pipeline,
                    color=shapes.GRAY,
                    scale=[10, 10, 10],
                    rotation=[-np.pi/2, 0, 0]
                )

    graph.add_node("wall_1",
                    attach_to="hangar",
                    mesh=square,
                    texture = bricks_texture,
                    material = bricks_material,
                    pipeline = textured_mesh_lit_pipeline,
                    color=shapes.BROWN,
                    scale=[10, 5, 5],
                    position=[0, 2.5, -5]
                )
    graph.add_node("wall_2",
                    attach_to="hangar",
                    mesh=square,
                    texture = bricks_texture,
                    material = bricks_material,
                    pipeline = textured_mesh_lit_pipeline,
                    color=shapes.DARK_BLUE,
                    scale=[10, 5, 5],
                    position=[5, 2.5, 0],
                    rotation=[0, -np.pi/2, 0]
                )
    graph.add_node("wall_3",
                    attach_to="hangar",
                    mesh=square, 
                    texture = bricks_texture,
                    material = bricks_material,
                    pipeline = textured_mesh_lit_pipeline,
                    color=shapes.BROWN,
                    scale=[10, 5, 5],
                    position=[0, 2.5, 5],
                    rotation=[0, -np.pi, 0]
                )
    graph.add_node("wall_4", 
                    attach_to="hangar",
                    mesh=square, 
                    texture = bricks_texture,
                    material = bricks_material,
                    pipeline = textured_mesh_lit_pipeline,
                    color=shapes.DARK_BLUE,
                    scale=[10, 5, 5],
                    position=[-5, 2.5, 0],
                    rotation=[0, -3*np.pi/2, 0]
                )
        
    graph.add_node("ceiling",
                    attach_to="hangar",
                    mesh=square, 
                    pipeline = textured_mesh_lit_pipeline,
                    texture = no_texture,
                    material = bricks_material,
                    color=shapes.GRAY,
                    scale=[10, 10, 10],
                    rotation=[np.pi/2, 0, 0],
                    position=[0, 5, 0]
                )

    graph.add_node("platform",
                    attach_to="floor",
                    mesh=cylinder, 
                    pipeline = color_mesh_lit_pipeline,
                    material = reflective_material,
                    color=shapes.BLACK,
                    position=[0, 0, -0.2],
                    scale=[0.5, 0.5, 0.5],
                    rotation=[np.pi/2, 0, 0]
                )

    graph.add_node("top_light",
                    attach_to="ceiling",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[0, 0, 0.1],
                    rotation=[0, np.pi, 0],
                    light=PointLight(
                        diffuse = [0.5, 0.5, 0.5],
                        specular = [0.5, 0.5, 0.5],
                        ambient = [0.9, 0.9, 0.9],
                        linear = 0.7,
                        )
                    )

    
    graph.add_node("bottom_light_1",
                    attach_to="floor",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    light=PointLight(
                        diffuse = [0.5, 0.5, 0.5],
                        specular = [0.5, 0.5, 1],
                        ambient = [1, 1, 1],
                        #constant = 1.0,
                        linear = 0.7,
                        #quadratic = 1.8
                        )
                    )

    graph.add_node("bottom_light_2",
                    attach_to="floor",
                    pipeline=textured_mesh_lit_pipeline,
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    light=PointLight(
                        diffuse = [0.1, 0.1, 0.1],
                        specular = [0, 0, 1],
                        ambient = [0, 0, 0],
                        #constant = 1.0,
                        linear = 0.7,
                        #quadratic = 1.8
                        )
                    )


def make_car(graph):

    graph.add_node("car", attach_to="platform")

    graph.add_node("car_chassis",
                                attach_to="car",
                                mesh= chassis_mesh,
                                material = car_material_0,
                                pipeline = textured_mesh_lit_pipeline,
                                texture = car_texture,
                                color=shapes.RED,
                                position=[0, 0.7, 0],
                                scale=[0.5, 0.5, 0.5]
                            )
    graph.add_node("car_wheel_front_right",
                                attach_to="car_chassis",
                                mesh= wheel_mesh,
                                material = wheel_material,
                                pipeline = textured_mesh_lit_pipeline,
                                texture = wheel_texture,
                                color=shapes.BLACK,
                                position=[0.48, -0.09, 0.45],
                                scale=[0.19, 0.19, 0.19]
                            )
    graph.add_node("car_wheel_front_left",
                                attach_to="car_chassis",
                                mesh= wheel_mesh,
                                material = wheel_material,
                                pipeline = textured_mesh_lit_pipeline,
                                texture = wheel_texture,
                                color=shapes.BLACK,
                                position=[0.48, -0.09, -0.45],
                                scale=[0.19, 0.19, -0.19]
                                )
    graph.add_node("car_wheel_back_right",
                                attach_to="car_chassis",
                                mesh=wheel_mesh,
                                material = wheel_material,
                                pipeline = textured_mesh_lit_pipeline,
                                texture = wheel_texture,
                                color=shapes.BLACK,
                                position=[-0.57, -0.09, 0.45],
                                scale=[0.19, 0.19, 0.19]
                                )
    graph.add_node("car_wheel_back_left",
                                attach_to="car_chassis",
                                mesh=wheel_mesh,
                                material = wheel_material,
                                pipeline = textured_mesh_lit_pipeline,
                                texture = wheel_texture,
                                color=shapes.BLACK,
                                position=[-0.57, -0.09, -0.45],
                                scale=[0.19, 0.19, -0.19]
                                )

if __name__ == "__main__":
    # Preparar Controller
    controller = Controller("Tarea 2", width=WIDTH, height=HEIGHT, resizable=True)
    
    # Preparar Pipelines
    color_mesh_pipeline = init_pipeline(
        get_path("shaders/color_mesh.vert"),
        get_path("shaders/color_mesh.frag"))

    color_mesh_lit_pipeline = init_pipeline(
        get_path("shaders/color_mesh_lit.vert"),
        get_path("shaders/color_mesh_lit.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("shaders/textured_mesh.vert"),
        get_path("shaders/textured_mesh.frag"))

    textured_mesh_lit_pipeline = init_pipeline(
        get_path("shaders/textured_mesh_lit.vert"),
        get_path("shaders/textured_mesh_lit.frag"))

    # Instancia de la cámara
    controller.program_state["camera"] = FreeCamera([5.5,5.5,5.5], "perspective")
    controller.program_state["camera"].yaw = -3* np.pi/ 4
    controller.program_state["camera"].pitch = -np.pi / 4

    axis_scene = init_axis(controller)
    # Instancia de las luces
    controller.program_state["light"] = DirectionalLight()

    # Definir Modelos
    square = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    cylinder = mesh_from_file(get_path("assets/cylinder.off"))[0]["mesh"]
    chassis_mesh = mesh_from_file(get_path("assets/chassis.obj"))[0]["mesh"]
    wheel_mesh = mesh_from_file(get_path("assets/wheel.obj"))[0]["mesh"]

    # Definir texturas
    bricks_texture = Texture(get_path("assets/bricks.jpg"))
    concrete_texture = Texture(get_path("assets/concrete1.jpg"))
    car_texture = mesh_from_file(get_path("assets/chassis.obj"))[0]["texture"]
    wheel_texture = mesh_from_file(get_path("assets/wheel.obj"))[0]["texture"]
    no_texture = Texture()

    # Definir Materiales
    concrete_material = Material(
            diffuse = [1, 1, 1],
            specular = [0, 0, 0],
            ambient = [1, 1, 1],
            shininess = 20)
    
    bricks_material = Material(
            diffuse = [0.2, 0.2, 0.2],
            specular = [0, 0, 0],
            ambient = [0.5, 0.5, 0.5],
            shininess = 20)
    
    reflective_material = Material(
            diffuse = [0.5, 0.5, 0.5],
            specular = [0.5, 0.5, 0.5],
            ambient = [0.5, 0.5, 0.5],
            shininess = 80)

    car_material_0 = Material(
            diffuse = [0.5, 0.5, 0.5],
            specular = [0.5, 0.5, 1],
            ambient = [0.5, 0.5, 0.5],
            shininess = 80)

    car_material_1 = Material(
            diffuse = [0, 0.5, 0.5],
            specular = [0.5, 0.5, 0.5],
            ambient = [0.5, 0.5, 0.5],
            shininess = 30)
    
    car_material_2 = Material(
            diffuse = [0.5, 0.5, 0.5],
            specular = [0.5, 0.5, 0.5],
            ambient = [0.5, 0.5, 0.5],
            shininess = 30)
    
    wheel_material = Material(
            diffuse = [1, 1, 1],
            specular = [0,0,0],
            ambient = [1, 1, 1],
            shininess = 5)

    # Ordenamos la escena en un grafo
    scene_graph = SceneGraph(controller)

    make_hangar(scene_graph)
    make_car(scene_graph)

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        scene_graph.draw()

    current_car = scene_graph["car"]
    @controller.event
    # Cambiar autos en ciclo
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            if scene_graph["car"]["material"] == car_material_0:
                scene_graph["car"]["material"] = car_material_1
            if scene_graph["car"]["material"] == car_material_1:
                scene_graph["car"]["material"] = car_material_2
            if scene_graph["car"]["material"] == car_material_2:
                scene_graph["car"]["material"] = car_material_0
            

    def update(dt):
        controller.program_state["total_time"] += dt
        platform_rotation = dt * 0.5
        scene_graph["car"]["rotation"][1] += platform_rotation
        camera = controller.program_state["camera"]
        camera.update()

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.RIGHT:
            controller.program_state["camera"].yaw += dx * 0.01
            controller.program_state["camera"].pitch += dy * 0.01
        
        if buttons & pyglet.window.mouse.LEFT:
            scene_graph["root"]["rotation"][0] += dy * 0.01
            scene_graph["root"]["rotation"][1] += dx * 0.01


    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    