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
from . import tiled_textures_mixer

def register():
    tiled_textures_mixer.register()

def unregister():
    tiled_textures_mixer.unregister()

if __name__ == "__main__":
    register()