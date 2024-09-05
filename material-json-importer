import bpy
import json
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

def set_socket_value(socket, value):
    if isinstance(value, (float, int, bool)):
        socket.default_value = value
    elif isinstance(value, list):
        if len(value) == len(socket.default_value):
            socket.default_value = value

def find_socket(node, socket_identifier, is_output=False):
    sockets = node.outputs if is_output else node.inputs
    for socket in sockets:
        if socket.identifier == socket_identifier:
            return socket
    return None

def create_node(material, node_data):
    node_type = node_data['type']
    try:
        node = material.node_tree.nodes.new(type=node_type)
    except:
        print(f"Warning: Node type '{node_type}' not found. Creating a NodeGroupInput instead.")
        node = material.node_tree.nodes.new(type='NodeGroupInput')
    
    node.name = node_data['name']
    node.location = node_data['location']
    
    if hasattr(node, 'width'):
        node.width = node_data.get('width', node.width)
    if hasattr(node, 'height'):
        node.height = node_data.get('height', node.height)
    
    for input_name, input_data in node_data['inputs'].items():
        socket = find_socket(node, input_name)
        if socket and 'default_value' in input_data:
            set_socket_value(socket, input_data['default_value'])

    for prop_name, prop_value in node_data.items():
        if prop_name not in ["name", "type", "location", "width", "height", "inputs", "outputs"]:
            if hasattr(node, prop_name):
                try:
                    setattr(node, prop_name, prop_value)
                except:
                    print(f"Warning: Could not set property '{prop_name}' for node '{node.name}'")

    return node

def create_material_from_json(json_data):
    material_name = json_data['name']
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material.node_tree.nodes.clear()

    nodes = {}
    for node_name, node_data in json_data['nodes'].items():
        nodes[node_name] = create_node(material, node_data)

    for link_data in json_data['links']:
        from_node = nodes.get(link_data['from_node'])
        to_node = nodes.get(link_data['to_node'])
        if from_node and to_node:
            from_socket = find_socket(from_node, link_data['from_socket'], is_output=True)
            to_socket = find_socket(to_node, link_data['to_socket'])
            if from_socket and to_socket:
                material.node_tree.links.new(from_socket, to_socket)
            else:
                print(f"Warning: Could not create link from {link_data['from_node']}.{link_data['from_socket']} to {link_data['to_node']}.{link_data['to_socket']}")
        else:
            print(f"Warning: Could not create link. Node not found.")

    return material

class ImportMaterialOperator(Operator, ImportHelper):
    bl_idname = "import.material_json"
    bl_label = "Import Material from JSON"
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load JSON file: {str(e)}")
            return {'CANCELLED'}

        try:
            material = create_material_from_json(json_data)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import material: {str(e)}")
            return {'CANCELLED'}

        active_object = context.active_object
        if active_object and active_object.type == 'MESH':
            if active_object.data.materials:
                active_object.data.materials[0] = material
            else:
                active_object.data.materials.append(material)

        self.report({'INFO'}, f"Material '{material.name}' imported and applied to the active object")
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportMaterialOperator.bl_idname, text="Material from JSON (.json)")

def register():
    bpy.utils.register_class(ImportMaterialOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportMaterialOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()