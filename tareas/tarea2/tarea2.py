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

class Hangar():
    def __init__(self, controller):

        square = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
        cylinder = mesh_from_file(get_path("assets/cylinder.off"))[0]["mesh"]

        bricks_texture = Texture(get_path("assets/bricks.jpg"))
        concrete_texture = Texture(get_path("assets/concrete1.jpg"))
        ceiling_texture = Texture(get_path("assets/ceiling.jpg"))

        concrete_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.5,0.5,0.5],
            shininess = 10)
            
        bricks_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.5,0.5,0.5],
            shininess = 20)
            
        ceiling_material = Material(
            diffuse = [0.5,0.5,0.5],
            specular = [0.5,0.5,0.5],
            ambient = [0.5,0.5,0.5],
            shininess = 5)
            
        platform_material = Material(
            diffuse = [0.1,0.1,0.1],
            specular = [0.5,0.5,0.5],
            ambient = [0,0,0],
            shininess = 20)
            
        self.graph = SceneGraph(controller)
        self.graph.add_node("hangar",
                            attach_to="root", 
                        )
        self.graph.add_node("floor",
                            attach_to="hangar",
                            mesh=square,
                            texture = concrete_texture,
                            material = concrete_material,
                            pipeline = textured_mesh_lit_pipeline,
                            color=shapes.GRAY,
                            scale=[10,10,0],
                            rotation=[-np.pi/2, 0, 0]
                        )

        self.graph.add_node("wall_1",
                            attach_to="hangar",
                            mesh=square,
                            texture = bricks_texture,
                            material = bricks_material,
                            pipeline = textured_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[0, 2.5, -5]
                        )
        self.graph.add_node("wall_2",
                            attach_to="hangar",
                            mesh=square,
                            texture = bricks_texture,
                            material = bricks_material,
                            pipeline = textured_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[5, 2.5, 0],
                            rotation=[0, -np.pi/2, 0]
                        )
        self.graph.add_node("wall_3",
                            attach_to="hangar",
                            mesh=square, 
                            texture = bricks_texture,
                            material = bricks_material,
                            pipeline = textured_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[0, 2.5, 5],
                            rotation=[0, -np.pi, 0]
                        )
        self.graph.add_node("wall_4", 
                            attach_to="hangar",
                            mesh=square, 
                            texture = bricks_texture,
                            material = bricks_material,
                            pipeline = textured_mesh_lit_pipeline,
                            scale=[10, 5, 0],
                            position=[-5, 2.5, 0],
                            rotation=[0, -3*np.pi/2, 0]
                        )
            
        self.graph.add_node("ceiling",
                            attach_to="hangar",
                            mesh=square, 
                            texture = ceiling_texture,
                            pipeline = color_mesh_lit_pipeline,
                            material = bricks_material,
                            color=shapes.GRAY,
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
                                diffuse = [1,1,1],
                                specular = [5,5,5],
                                ambient = [2,2,2],
                                )
                            )

        self.graph.add_node("top_spotlight",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[0,3.9,0],
                            rotation=[-np.pi/2,0,0],
                            light=SpotLight(
                                diffuse = [0.5,0.5,0.5],
                                specular = [1,1,1],
                                ambient = [0.5,0.5,0.5],
                                cutOff = 1.5, # siempre mayor a outerCutOff
                                outerCutOff = 0.5
                                )
                            )
        
        self.graph.add_node("blue_spotlight",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[2,0,0],
                            rotation=[-np.pi/2,0,0],
                            light=SpotLight(
                                diffuse = [0.5,0.5,0.5],
                                specular = [1,1,1],
                                ambient = [0.5,0.5,0.5],
                                cutOff = 1.5, # siempre mayor a outerCutOff
                                outerCutOff = 0.5
                                )
                            )
        
        self.graph.add_node("green_spotlight",
                            attach_to = "hangar",
                            pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                            position=[0,0,-2],
                            rotation=[-np.pi/2,0,0],
                            light=SpotLight(
                                diffuse = [0.5,0.5,0.5],
                                specular = [1,1,1],
                                ambient = [0.5,0.5,0.5],
                                cutOff = 1.5, # siempre mayor a outerCutOff
                                outerCutOff = 0.5
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
                            color=shapes.BLACK,
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
                    specular = [0,0, 1],
                    ambient = [0.5,0.1,0.1],
                    shininess = 20
                    )
    
        blue = Material(
                        diffuse = [0.5,0.5,0.5],
                        specular = [0,10, 0],
                        ambient = [0.1,0.1,0.5],
                        shininess = 20
                        )
        
        green = Material(
                        diffuse = [0.2,0.2,0.2],
                        specular = [1,0,0],
                        ambient = [0.1,0.5,0.1],
                        shininess = 20
                        )

        self.material_list = [red, blue, green]

        wheel_material = Material(
                diffuse = [0.5,0.5,0.5],
                specular = [0,0,0],
                ambient = [0,0,0],
                shininess = 5)


        self.graph.add_node("car", attach_to="platform")
        self.graph.add_node("car_chassis",
                                    attach_to="car",
                                    mesh= chassis_mesh,
                                    material = red,
                                    texture = chassis_texture,
                                    pipeline = color_mesh_lit_pipeline,
                                    color=shapes.RED,
                                    position=[0, 0.2, 0],
                                    scale=[0.5, 0.5, 0.5]
                                )
        self.graph.add_node("car_wheel_front_right",
                                    attach_to="car_chassis",
                                    mesh= wheel_mesh,
                                    material = wheel_material,
                                    pipeline = color_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    color=shapes.BLACK,
                                    position=[0.48, -0.09, 0.45],
                                    scale=[0.19, 0.19, 0.19]
                                )
        self.graph.add_node("car_wheel_front_left",
                                    attach_to="car_chassis",
                                    mesh= wheel_mesh,
                                    material = wheel_material,
                                    pipeline = color_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    color=shapes.BLACK,
                                    position=[0.48, -0.09, -0.45],
                                    scale=[0.19, 0.19, -0.19]
                                    )
        self.graph.add_node("car_wheel_back_right",
                                    attach_to="car_chassis",
                                    mesh=wheel_mesh,
                                    material = wheel_material,
                                    pipeline = color_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    color=shapes.BLACK,
                                    position=[-0.57, -0.09, 0.45],
                                    scale=[0.19, 0.19, 0.19]
                                    )
        self.graph.add_node("car_wheel_back_left",
                                    attach_to="car_chassis",
                                    mesh=wheel_mesh,
                                    material = wheel_material,
                                    pipeline = color_mesh_lit_pipeline,
                                    texture = wheel_texture,
                                    color=shapes.BLACK,
                                    position=[-0.57, -0.09, -0.45],
                                    scale=[0.19, 0.19, -0.19]
                                    )
    def update(self,dt):
        platform_rotation = dt * 0.5
        self.graph["platform"]["rotation"][1] += platform_rotation

    def draw(self):
        self.graph.draw()

    def change_car_material(self):
        self.current_material += 1
        if self.current_material > 2:
            self.current_material = 0
        print(self.current_material)
        self.graph["car_chassis"]["material"] = self.material_list[self.current_material]

if __name__ == "__main__":
    # Preparar Controller
    controller = Controller("Tarea 2", width=WIDTH, height=HEIGHT, resizable=True)

    # Preparar Pipelines
    color_mesh_pipeline = init_pipeline(
        get_path("shaders/color_mesh.vert"),
        get_path("shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("shaders/textured_mesh.vert"),
        get_path("shaders/textured_mesh.frag"))

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

    # Ordenamos la escena en un grafo
    axis_scene = init_axis(controller)
    graph = SceneGraph(controller)
    hangar = Hangar(controller)

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        axis_scene.draw()
        hangar.draw()
    
    @controller.event
    # Cambiar autos en ciclo
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            hangar.change_car_material()

    def update(dt):
        controller.program_state["total_time"] += dt
        hangar.update(dt)
        camera = controller.program_state["camera"]
        camera.update()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    