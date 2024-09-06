import bpy
import os
import json
from bpy.props import StringProperty, FloatVectorProperty

def load_image(image_path, image_name):
    if os.path.exists(image_path):
        image = bpy.data.images.load(image_path, check_existing=True)
        image.reload()
        return image
    else:
        print(f"Image not found: {image_path}")
        return None

def create_tiled_material(context):
    mat = bpy.data.materials.new(name="Tiled Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    addon_dir = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(addon_dir, "material_node_structure.json")
    with open(json_path, "r") as f:
        node_data = json.load(f)

    node_type_mapping = {
        "SEPARATE_COLOR": "ShaderNodeSeparateColor",
        "MIX": "ShaderNodeMixRGB",
        "TEX_IMAGE": "ShaderNodeTexImage",
        "OUTPUT_MATERIAL": "ShaderNodeOutputMaterial",
        "BSDF_PRINCIPLED": "ShaderNodeBsdfPrincipled",
        "NORMAL_MAP": "ShaderNodeNormalMap",
        "TEX_COORD": "ShaderNodeTexCoord",
        "MAPPING": "ShaderNodeMapping",
        "UVMAP": "ShaderNodeUVMap"
    }

    created_nodes = {}

    for node in node_data["nodes"]:
        node_type = node_type_mapping.get(node["type"], node["type"])
        new_node = nodes.new(type=node_type)
        new_node.name = node["name"]
        new_node.location = node["location"]
        created_nodes[node["name"]] = new_node

        if node["type"] == "TEX_IMAGE":
            if "image" in node:
                image_name = node["image"]
                texture_path_prop = f"{new_node.name}_path"
                setattr(bpy.types.Scene, texture_path_prop, StringProperty(name=f"Path for {image_name}"))
                new_node["texture_path_prop"] = texture_path_prop
        elif node["type"] == "MAPPING":
            if "vector_type" in node:
                new_node.vector_type = node["vector_type"]
                
    def find_socket(node, socket_name, is_output=True):
        sockets = node.outputs if is_output else node.inputs
        for socket in sockets:
            if socket.name.lower() == socket_name.lower():
                return socket
        return None

    for link in node_data["links"]:
        from_node = created_nodes[link["from_node"]]
        to_node = created_nodes[link["to_node"]]
        from_socket = find_socket(from_node, link["from_socket"], is_output=True)
        to_socket = find_socket(to_node, link["to_socket"], is_output=False)

        if from_socket and to_socket:
            try:
                links.new(from_socket, to_socket)
            except Exception as e:
                print(f"Error creating link: {e}")
                print(f"From node: {from_node.name}, socket: {from_socket.name}")
                print(f"To node: {to_node.name}, socket: {to_socket.name}")
        else:
            print(f"Error creating link: {link}")
            print(f"From node: {from_node.name}, available outputs: {[s.name for s in from_node.outputs]}")
            print(f"To node: {to_node.name}, available inputs: {[s.name for s in to_node.inputs]}")

    material_output = next((node for node in created_nodes.values() if node.type == 'OUTPUT_MATERIAL'), None)
    if material_output:
        mat.node_tree.nodes.active = material_output

    return mat

class MATERIAL_OT_create_tiled_material(bpy.types.Operator):
    bl_idname = "material.create_tiled_material"
    bl_label = "Create Tiled Material"
    
    def execute(self, context):
        obj = context.active_object
        if obj:
            mat = create_tiled_material(context)
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
        return {'FINISHED'}

class MATERIAL_OT_load_texture(bpy.types.Operator):
    bl_idname = "material.load_texture"
    bl_label = "Load Texture"
    
    filepath: StringProperty(subtype="FILE_PATH")
    node_name: StringProperty()
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        material = context.object.active_material
        if not material:
            self.report({'ERROR'}, "No active material")
            return {'CANCELLED'}

        nodes = material.node_tree.nodes
        node = nodes.get(self.node_name)
        if not node:
            self.report({'ERROR'}, f"Node {self.node_name} not found")
            return {'CANCELLED'}

        image = load_image(self.filepath, os.path.basename(self.filepath))
        if image:
            node.image = image

            texture_path_prop = node.get("texture_path_prop")
            if texture_path_prop:
                setattr(context.scene, texture_path_prop, self.filepath)
        else:
            self.report({'ERROR'}, f"Failed to load image: {self.filepath}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MATERIAL_PT_tiled_material(bpy.types.Panel):
    bl_label = "Tiled Material"
    bl_idname = "MATERIAL_PT_tiled_material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.operator("material.create_tiled_material", text="Create Tiled Material")
        
        material = context.object.active_material
        if material:
            nodes = material.node_tree.nodes
            for node in nodes:
                if node.type == 'TEX_IMAGE':
                    row = layout.row()
                    row.label(text=node.name)
                    texture_path_prop = node.get("texture_path_prop")
                    if texture_path_prop:
                        row.prop(scene, texture_path_prop, text="")
                    op = row.operator("material.load_texture", text="", icon='FILE_FOLDER')
                    op.node_name = node.name
            
            layout.label(text="Tile Scales:")
            mapping_node = nodes.get("Mapping")
            if mapping_node:
                scale = mapping_node.inputs['Scale']
                layout.prop(scale, "default_value", text="Tile Scale")

def update_tile_scale(self, context):
    material = context.object.active_material
    if material and material.node_tree:
        mapping_node = material.node_tree.nodes.get("Mapping")
        if mapping_node:
            scale = mapping_node.inputs['Scale']
            scale.default_value = self.tile_scale

class TiledMaterialProperties(bpy.types.PropertyGroup):
    tile_scale: FloatVectorProperty(
        name="Tile Scale",
        description="Scale of the tiled texture",
        default=(1.0, 1.0, 1.0),
        min=0.1,
        max=10.0,
        update=update_tile_scale
    )

def register():
    bpy.utils.register_class(MATERIAL_OT_create_tiled_material)
    bpy.utils.register_class(MATERIAL_OT_load_texture)
    bpy.utils.register_class(MATERIAL_PT_tiled_material)
    bpy.utils.register_class(TiledMaterialProperties)
    bpy.types.Scene.tiled_material = bpy.props.PointerProperty(type=TiledMaterialProperties)

def unregister():
    bpy.utils.unregister_class(MATERIAL_OT_create_tiled_material)
    bpy.utils.unregister_class(MATERIAL_OT_load_texture)
    bpy.utils.unregister_class(MATERIAL_PT_tiled_material)
    bpy.utils.unregister_class(TiledMaterialProperties)
    del bpy.types.Scene.tiled_material

if __name__ == "__main__":
    register()