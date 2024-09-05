import bpy
import json
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator

def serialize_socket(socket):
    socket_data = {
        "name": socket.name,
        "identifier": socket.identifier,
        "type": socket.type
    }
    if hasattr(socket, "default_value"):
        if isinstance(socket.default_value, (float, int, bool)):
            socket_data["default_value"] = socket.default_value
        elif hasattr(socket.default_value, "__len__"):
            socket_data["default_value"] = list(socket.default_value)
    return socket_data

def serialize_node(node):
    node_data = {
        "name": node.name,
        "type": node.bl_idname,
        "location": list(node.location),
        "width": node.width,
        "height": node.height,
        "use_custom_color": node.use_custom_color,
        "color": list(node.color),
        "inputs": {},
        "outputs": {},
    }
    
    for input in node.inputs:
        node_data["inputs"][input.identifier] = serialize_socket(input)
    
    for output in node.outputs:
        node_data["outputs"][output.identifier] = serialize_socket(output)
    
    # Сохраняем дополнительные свойства нода
    for prop_name, prop in node.bl_rna.properties.items():
        if prop.is_runtime or prop_name in ["name", "type", "inputs", "outputs"]:
            continue
        if hasattr(node, prop_name):
            value = getattr(node, prop_name)
            if isinstance(value, (float, int, bool, str)):
                node_data[prop_name] = value
            elif hasattr(value, "to_list"):
                node_data[prop_name] = value.to_list()
    
    return node_data

def serialize_material(material):
    nodes_data = {}
    links_data = []
    
    for node in material.node_tree.nodes:
        nodes_data[node.name] = serialize_node(node)
    
    for link in material.node_tree.links:
        links_data.append({
            "from_node": link.from_node.name,
            "from_socket": link.from_socket.identifier,
            "to_node": link.to_node.name,
            "to_socket": link.to_socket.identifier
        })
    
    return {
        "name": material.name,
        "nodes": nodes_data,
        "links": links_data
    }

class ExportMaterialOperator(Operator, ExportHelper):
    bl_idname = "export.material_json"
    bl_label = "Export Material as JSON"
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        material = context.active_object.active_material
        if not material:
            self.report({'ERROR'}, "No active material found")
            return {'CANCELLED'}
        
        material_data = serialize_material(material)
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(material_data, f, indent=4)
        
        self.report({'INFO'}, f"Material exported to {self.filepath}")
        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(ExportMaterialOperator.bl_idname, text="Material as JSON (.json)")

def register():
    bpy.utils.register_class(ExportMaterialOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportMaterialOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()