import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
from pathlib import Path
from scenes.circuit import Circuit

# No es necesaria la siguiente línea si el archivo está en el root del repositorio
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import grafica.transformations as tr
import utils.shapes as shapes
from utils.camera import OrbitCamera
from utils.scene_graph import SceneGraph
from utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

class Hangar():
    def __init__(self, scene_controller, textured_mesh_lit_pipeline, color_mesh_lit_pipeline):
        # Definir pipeline
        self.scene_controller = scene_controller
        self.controller = scene_controller.controller
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
            
        self.graph = SceneGraph(self.controller)
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
            position=[0, 0.1, 0],
            scale=[0.5,0.5,0.5]
        )

        self.graph.add_node("car_chassis",
                                    attach_to="car",
                                    mesh= chassis_mesh,
                                    material = red,
                                    texture = chassis_texture,
                                    pipeline = textured_mesh_lit_pipeline,
                                    position=[0, 0.2, 0],
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

        # Instancia de la cámara
        self.controller.program_state["camera"] = OrbitCamera(5.5, "perspective")
        self.controller.program_state["camera"].phi = np.pi / 4
        self.controller.program_state["camera"].theta = 3*(np.pi) / 8
        
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
            self.nextScene()

    def change_car_material(self):
        self.current_material += 1
        if self.current_material > 2:
            self.current_material = 0
        print(self.current_material)
        self.graph["car_chassis"]["material"] = self.material_list[self.current_material]

    def nextScene(self):
        car_material = self.graph["car_chassis"]["material"]
        circuit = Circuit(self.scene_controller, 
                self.textured_mesh_lit_pipeline, 
                self.color_mesh_lit_pipeline, 
                car_material
                )
        self.scene_controller.scene = circuit


