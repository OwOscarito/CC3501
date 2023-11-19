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

class Hangar():
    def __init__(self, controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline):
        # Definir pipeline
        self.controller = controller
        self.textured_mesh_lit_pipeline = textured_mesh_lit_pipeline
        self.color_mesh_lit_pipeline = color_mesh_lit_pipeline

        square = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
        cylinder = mesh_from_file(get_path("assets/cylinder.off"))[0]["mesh"]
        
        floor_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.1,0.1,0.1],
            shininess = 10)
            
        wall_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.5,0.3,0.1],
            shininess = 20)
            
        ceiling_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.4,0.4,0.4],
            shininess = 5)
            
        platform_material = Material(
            diffuse = [0.1,0.1,0.1],
            specular = [0.5,0.5,0.5],
            ambient = [0.6,0.6,0.6],
            shininess = 50)
            
        self.graph = SceneGraph(controller)
        self.graph.add_node("hangar",
                            attach_to="root", 
                        )
        self.graph.add_node("floor",
                            attach_to="hangar",
                            mesh=square,
                            material = floor_material,
                            pipeline = color_mesh_lit_pipeline,
                            color=shapes.GRAY,
                            scale=[10,10,0],
                            rotation=[-np.pi/2, 0, 0]
                        )

        self.graph.add_node("wall_1",
                            attach_to="hangar",
                            mesh=square,
                            material = wall_material,
                            pipeline = color_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[0, 2.5, -5]
                        )
        self.graph.add_node("wall_2",
                            attach_to="hangar",
                            mesh=square,
                            material = wall_material,
                            pipeline = color_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[5, 2.5, 0],
                            rotation=[0, -np.pi/2, 0]
                        )
        self.graph.add_node("wall_3",
                            attach_to="hangar",
                            mesh=square, 
                            material = wall_material,
                            pipeline = color_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[0, 2.5, 5],
                            rotation=[0, -np.pi, 0]
                        )
        self.graph.add_node("wall_4", 
                            attach_to="hangar",
                            mesh=square, 
                            material = wall_material,
                            pipeline = color_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[-5, 2.5, 0],
                            rotation=[0, -3*np.pi/2, 0]
                        )
            
        self.graph.add_node("ceiling",
                            attach_to="hangar",
                            mesh=square, 
                            pipeline = color_mesh_lit_pipeline,
                            material = ceiling_material,
                            scale=[10,10, 0],
                            rotation=[np.pi/2, 0, 0],
                            position=[0, 5, 0]
                    )

        self.graph.add_node("ambient_light",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[0,3.8,0],
                            rotation=[0,0,0],
                            light=PointLight(
                                diffuse = [0,0,0],
                                specular = [0,0,0],
                                ambient = [1.5,1.5,1.5],
                                )
                            )

        self.graph.add_node("top_spotlight",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[0,4.9,0],
                            rotation=[-np.pi/2,0,0],
                            light=SpotLight(
                                diffuse = [1,1,1],
                                specular = [5,2,2],
                                ambient = [0,0,0],
                                cutOff = 0.8,
                                outerCutOff = 1
                                )
                            )

        self.graph.add_node("spotlight_verde",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[5,0,0],
                            rotation=[-np.pi/2,0,0],
                            light=SpotLight(
                                diffuse = [0.5,0.5,0.5],
                                specular = [0,5,0],
                                ambient = [0,0,0],
                                cutOff = 0.8,
                                outerCutOff = 1
                                )
                            )

        self.graph.add_node("spotlight_roja",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[0,0,5],
                            rotation=[-np.pi/4,np.pi/2,0],
                            light=SpotLight(
                                diffuse = [0.5,0.5,0.5],
                                specular = [5,0,0],
                                ambient = [0,0,0],
                                cutOff = 0.8,
                                outerCutOff = 1
                                )
                            )

        self.graph.add_node("spotlight_azul",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[5,0,5],
                            rotation=[-np.pi/4,3*np.pi/4,0],
                            light=SpotLight(
                                diffuse = [0.5,0.5,0.5],
                                specular = [0,0,5],
                                ambient = [0,0,0],
                                cutOff = 0.8,
                                outerCutOff = 1
                                )
                            )

        self.graph.add_node("platform",
                            attach_to="hangar",
                            scale = [5,5,5]
                            )
                        
        self.graph.add_node("cylinder",
                            attach_to="platform",
                            mesh=cylinder, 
                            pipeline = color_mesh_lit_pipeline,
                            material = platform_material,
                            color=shapes.WHITE,
                            position=[0, 0, 0],
                            scale=[1, 0.1, 1],
                            )

        # Definir Modelos
        chassis = mesh_from_file(get_path("assets/LamboChassis.obj"))
        chassis_mesh= chassis[0]["mesh"]
        chassis_texture = chassis[0]["texture"]

        wheel = mesh_from_file(get_path("assets/LamboWheel.obj"))
        wheel_mesh= wheel[0]["mesh"]
        wheel_texture = wheel[0]["texture"]

        # Definir Materiales
        self.current_material = 0
        red = Material(
                    diffuse = [0.5,0.5,0.5],
                    specular = [0,1, 0],
                    ambient = [0.5,0.1,0.1],
                    shininess = 40
                    )
    
        blue = Material(
                        diffuse = [0.5,0.5,0.5],
                        specular = [1,0, 0],
                        ambient = [0.1,0.1,0.5],
                        shininess = 20
                        )
        
        green = Material(
                        diffuse = [0.2,0.2,0.2],
                        specular = [0,0,1],
                        ambient = [0.1,0.5,0.1],
                        shininess = 20
                        )

        self.material_list = [red, blue, green]

        wheel_material = Material(
                diffuse = [0.5,0.5,0.5],
                specular = [0,0,0],
                ambient = [0.1,0.1,0.1],
                shininess = 5)


        self.graph.add_node("car", 
            attach_to="platform", 
            position=[0, 0.2, 0],
            scale=[0.5,0.5,0.5]
        )

        self.graph.add_node("car_chassis",
                                    attach_to="car",
                                    mesh= chassis_mesh,
                                    material = red,
                                    texture = chassis_texture,
                                    pipeline = textured_mesh_lit_pipeline,
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

        self.controller.program_state["camera"].position = [4,2,4]
        self.controller.program_state["camera"].pitch = -np.pi/8
        self.controller.program_state["camera"].yaw = -3*np.pi/4

    def update(self,dt):
        platform_rotation = dt * 0.5
        self.graph["platform"]["rotation"][1] += platform_rotation
        camera = self.controller.program_state["camera"]
        camera.update()

    def draw(self):
        self.graph.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.change_car_material()
        if symbol == pyglet.window.key.ENTER:
            self.next_scene()

    def change_car_material(self):
        self.current_material += 1
        if self.current_material > 2:
            self.current_material = 0
        print(self.current_material)
        self.graph["car_chassis"]["material"] = self.material_list[self.current_material]

    def next_scene(self):
        car_material = self.graph["car_chassis"]["material"]
        self.controller.change_scene(Circuit(self.controller, 
                self.textured_mesh_lit_pipeline, 
                self.color_mesh_lit_pipeline, 
                car_material
            )
        )


class Circuit():
    def __init__(self, controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline, material):

        self.controller = controller
        self.textured_mesh_lit_pipeline = textured_mesh_lit_pipeline
        self.color_mesh_lit_pipeline = color_mesh_lit_pipeline

        square = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
        cylinder = mesh_from_file(get_path("assets/cylinder.off"))[0]["mesh"]
        floor_texture = Texture(get_path("assets/circuit.png"))

        floor_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0,0,0],
            ambient = [0.5,0.5,0.5],
            shininess = 10
            )
        self.graph = SceneGraph(self.controller)
        self.graph.add_node("circuit",
                            attach_to="root", 
                        )
        self.graph.add_node("circuit_floor",
                            attach_to="circuit",
                            pipeline= self.textured_mesh_lit_pipeline,
                            mesh= square,
                            material= floor_material,
                            texture= floor_texture,
                            scale=[100,100,0],
                            rotation=[-np.pi/2, 0, 0],
                            position=[0, 0, 0]
                        )
        self.graph.add_node("sun",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    position=[0, 10, 0],
                    rotation=[-np.pi/4, 0, 0],
                    light=DirectionalLight(diffuse = [1, 1, 1], specular = [0.25, 0.25, 0.25], ambient = [0.5,0.5,0.5]))

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
                ambient = [0.1,0.1,0.1],
                shininess = 5)

        self.graph.add_node("car", 
            position=[0, 0, 0],
            scale=[0.5,0.5,0.5]
        )
        self.graph.add_node("car_chassis",
                                    attach_to="car",
                                    mesh= chassis_mesh,
                                    material = material,
                                    texture = chassis_texture,
                                    pipeline = textured_mesh_lit_pipeline,
                                    position=[0, 0, 0],
                                    rotation=[0, -np.pi/2, 0]
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
        ########## Simulación Física ##########
        world = b2World(gravity=(0, 0))

        # Objetos dinámicos
        car_body = world.CreateDynamicBody(position=(0, 0))
        car_body.CreatePolygonFixture(box=(0.5, 0.5), density=1, friction=2)

        # Se guardan los cuerpos en el self.controller para poder acceder a ellos desde el loop de simulación
        self.controller.program_state["world"] = world
        self.controller.program_state["bodies"]["car"] = car_body
        #######################################

    # Aquí se actualizan los parámetros de la simulación física
    def update_world(self, dt):
        world = self.controller.program_state["world"]
        world.Step(dt,
            self.controller.program_state["vel_iters"], 
            self.controller.program_state["pos_iters"]
        )
        world.ClearForces()

    def update(self, dt):
        # Actualización física del auto
        car_body = self.controller.program_state["bodies"]["car"]
        self.graph["car"]["transform"] = tr.translate(car_body.position[0], 0, car_body.position[1]) @ tr.rotationY(-car_body.angle)
        camera = self.controller.program_state["camera"]
        camera.position[0] = car_body.position[0] + 2 * np.sin(car_body.angle)
        camera.position[1] = 2
        camera.position[2] = car_body.position[1] - 2 * np.cos(car_body.angle)
        camera.yaw = car_body.angle + np.pi / 2
        camera.update()
        self.update_world(dt)
    
    def on_key_press(self, symbol, modifiers):
        car_body = self.controller.program_state["bodies"]["car"]
        # Modificar la fuerza y el torque del car con las teclas
        car_forward = np.array([np.sin(-car_body.angle), 0, np.cos(-car_body.angle)])
    def on_key_press(self, symbol, modifiers):
        car_body = self.controller.program_state["bodies"]["car"]
        # Reset car
        if symbol == pyglet.window.key.SPACE:
            car_body.position = (0, -5)
            car_body.angle = 0
            car_body.linearVelocity = (0, 0)
            car_body.angularVelocity = 0
        if symbol == pyglet.window.key.ENTER:
            self.next_scene()

    def draw(self):
        self.graph.draw()
    
    def next_scene(self):
        self.controller.change_scene(Hangar(self.controller, 
                self.textured_mesh_lit_pipeline, 
                self.color_mesh_lit_pipeline, 
                ))