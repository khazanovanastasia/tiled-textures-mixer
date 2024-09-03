bl_info = {
    "name": "Tiled Material Creator",
    "author": "khazanovanastasia",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "Properties > Material > Tiled Material",
    "description": "Creates and manages tiled materials",
    "warning": "",
    "doc_url": "",
    "category": "Material",
}

import bpy
from . import tiled_material_addon

def register():
    tiled_material_addon.register()

def unregister():
    tiled_material_addon.unregister()

if __name__ == "__main__":
    register()