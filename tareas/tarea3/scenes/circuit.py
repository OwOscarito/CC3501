import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
from Box2D import b2PolygonShape, b2World

# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import grafica.transformations as tr
import utils.shapes as shapes
from utils.camera import OrbitCamera, FreeCamera
from utils.scene_graph import SceneGraph
from utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

class Circuit():
    def __init__(self, controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline, material):

        self.controller = controller
        self.textured_mesh_lit_pipeline = textured_mesh_lit_pipeline
        self.color_mesh_lit_pipeline = color_mesh_lit_pipeline

        square = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
        cylinder = mesh_from_file(get_path("assets/cylinder.off"))[0]["mesh"]
        #floor_texture = Texture(get_path("assets/floor.png"), GL.GL_REPEAT, GL.GL_LINEAR)

        floor_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.1,0.1,0.1],
            shininess = 10
            )
        self.graph = SceneGraph(self.controller)
        self.graph.add_node("circuit",
                            attach_to="root", 
                        )
        self.graph.add_node("circuit_floor",
                            attach_to="circuit",
                            pipeline= self.color_mesh_lit_pipeline,
                            mesh= square,
                            material= floor_material,
                            color=shapes.GRAY,
                            scale=[50,50,0],
                            rotation=[-np.pi/2, 0, 0]
                        )
        self.graph.add_node("sun",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    position=[0, 2, 0],
                    rotation=[-np.pi/4, 0, 0],
                    light=DirectionalLight(diffuse = [1, 1, 1], specular = [0.25, 0.25, 0.25], ambient = [0.15, 0.15, 0.15]))

        # Definir Modelos
        chassis = mesh_from_file(get_path("assets/LamboChassis.obj"))
        chassis_mesh= chassis[0]["mesh"]
        chassis_texture = chassis[0]["texture"]

        wheel = mesh_from_file(get_path("assets/LamboWheel.obj"))
        wheel_mesh= wheel[0]["mesh"]
        wheel_texture = wheel[0]["texture"]

        wheel_material = Material(
                diffuse = [0.5,0.5,0.5],
                specular = [0,0,0],
                ambient = [0,0,0],
                shininess = 5)

        self.graph.add_node("car")
        self.graph.add_node("car_chassis",
                                    attach_to="car",
                                    mesh= chassis_mesh,
                                    material = material,
                                    texture = chassis_texture,
                                    pipeline = color_mesh_lit_pipeline,
                                    position=[0, 1, 0],
                                    scale=[0.5, 0.5, 0.5]
                                )
        self.graph.add_node("car_wheel_front_right",
                                    attach_to="car_chassis",
                                    mesh= wheel_mesh,
                                    material = wheel_material,
                                    pipeline = textured_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    position=[0.48, -0.09, 0.45],
                                    scale=[0.19, 0.19, 0.19]
                                )
        self.graph.add_node("car_wheel_front_left",
                                    attach_to="car_chassis",
                                    mesh= wheel_mesh,
                                    material = wheel_material,
                                    pipeline = textured_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    position=[0.48, -0.09, -0.45],
                                    scale=[0.19, 0.19, -0.19]
                                    )
        self.graph.add_node("car_wheel_back_right",
                                    attach_to="car_chassis",
                                    mesh=wheel_mesh,
                                    material = wheel_material,
                                    pipeline = textured_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    position=[-0.57, -0.09, 0.45],
                                    scale=[0.19, 0.19, 0.19]
                                    )
        self.graph.add_node("car_wheel_back_left",
                                    attach_to="car_chassis",
                                    mesh=wheel_mesh,
                                    material = wheel_material,
                                    pipeline = textured_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    position=[-0.57, -0.09, -0.45],
                                    scale=[0.19, 0.19, -0.19]
                                    )

        controller.program_state["camera"] = FreeCamera([0, 0, 0], "perspective")
        controller.program_state["camera"].pitch = -np.pi / 8
        controller.program_state["camera"].yaw = np.pi / 2
        ########## Simulación Física ##########
        world = b2World(gravity=(0, -10), doSleep=True)

        # Objetos estáticos
        wall1_body = world.CreateStaticBody(position=(-10, 0))
        wall1_body.CreatePolygonFixture(box=(0.5, 10), density=1, friction=1)

        wall2_body = world.CreateStaticBody(position=(10, 0))
        wall2_body.CreatePolygonFixture(box=(0.5, 10), density=1, friction=1)

        wall3_body = world.CreateStaticBody(position=(0, -10))
        wall3_body.CreatePolygonFixture(box=(10, 0.5), density=1, friction=1)

        wall4_body = world.CreateStaticBody(position=(0, 10))
        wall4_body.CreatePolygonFixture(box=(10, 0.5), density=1, friction=1)

        # Objetos dinámicos
        car_body = world.CreateDynamicBody(position=(0, -5))
        car_body.CreatePolygonFixture(box=(0.5, 0.5), density=1, friction=1)

        # Se guardan los cuerpos en el self.controller para poder acceder a ellos desde el loop de simulación
        self.controller.program_state["world"] = world
        self.controller.program_state["bodies"]["car"] = car_body

        #######################################

    # Aquí se actualizan los parámetros de la simulación física
    def update_world(self, dt):
        world = self.controller.program_state["world"]
        world.Step(
            dt, self.controller.program_state["vel_iters"], self.controller.program_state["pos_iters"]
        )
        world.ClearForces()

    def update(self, dt):
        # Actualización física del auto
        car_body = self.controller.program_state["bodies"]["car"]
        self.graph["car"]["transform"] = tr.translate(car_body.position[0], 0, car_body.position[1]) @ tr.rotationY(-car_body.angle)

    
    def on_key_press(self, symbol, modifiers):
        car_body = self.controller.program_state["bodies"]["car"]
        # Modificar la fuerza y el torque del car con las teclas
        car_forward = np.array([np.sin(-car_body.angle), 0, np.cos(-car_body.angle)])
        if self.controller.is_key_pressed(pyglet.window.key.A):
            car_body.ApplyTorque(-0.5, True)
        if self.controller.is_key_pressed(pyglet.window.key.D):
            car_body.ApplyTorque(0.5, True)
        if self.controller.is_key_pressed(pyglet.window.key.W):
            car_body.ApplyForce((car_forward[0], car_forward[2]), car_body.worldCenter, True)
        if self.controller.is_key_pressed(pyglet.window.key.S):
            car_body.ApplyForce((-car_forward[0], -car_forward[2]), car_body.worldCenter, True)

        camera.position[0] = car_body.position[0] + 2 * np.sin(car_body.angle)
        camera.position[1] = 5
        camera.position[2] = car_body.position[1] - 2 * np.cos(car_body.angle)

        camera.yaw = car_body.angle + np.pi / 2
        camera.update()
        update_world(dt)

    def on_key_press(self, symbol, modifiers):
        car_body = self.controller.program_state["bodies"]["car"]
        # Reset car
        if symbol == pyglet.window.key.SPACE:
            car_body.position = (0, -5)
            car_body.angle = 0
            car_body.linearVelocity = (0, 0)
            car_body.angularVelocity = 0

    def draw(self):
        self.graph.draw()