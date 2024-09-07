import bpy
import os
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty, FloatProperty

class TextureProperties(PropertyGroup):
    @staticmethod
    def get_object_texture_path(filename):
        addon_directory = os.path.dirname(os.path.realpath(__file__))
        object_textures_directory = os.path.join(addon_directory, "Object_textures")
        return os.path.join(object_textures_directory, filename)

    texture_1: StringProperty(
        name="Texture 1",
        description="Path to texture file",
        default=get_object_texture_path("Albedo.tga"),
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_2: StringProperty(
        name="Texture 2",
        description="Path to texture file",
        default=get_object_texture_path("Metallic.tga"),
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_3: StringProperty(
        name="Texture 3",
        description="Path to texture file",
        default=get_object_texture_path("Normal Map.tga"),
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_4: StringProperty(
        name="Texture 4",
        description="Path to texture file",
        default=get_object_texture_path("Roughness.tga"),
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_9: StringProperty(
        name="Tile0_a",
        description="Path to Tile0_a texture file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_10: StringProperty(
        name="Tile1_a",
        description="Path to Tile1_a texture file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_11: StringProperty(
        name="Tile2_a",
        description="Path to Tile2_a texture file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    texture_12: StringProperty(
        name="Tile3_a",
        description="Path to Tile3_a texture file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    tile_scale: FloatProperty(
        name="Tile Scale",
        description="Scale of the tiled textures",
        default=1.0,
        min=0.1,
        max=10.0
    )

class CreateMaterial(Operator):
    bl_idname = "material.create"
    bl_label = "Create Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_absolute_path(self, path):
        if path.startswith("//"):
            return bpy.path.abspath(path)
        return path
    
    def execute(self, context):
        
        material = bpy.data.materials.new(name="BASE_Material")
        material.use_nodes = True

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        normal_map = nodes.new('ShaderNodeNormalMap')
        tex_coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        uv_map = nodes.new('ShaderNodeUVMap')

        tex_nodes = {}
        for i in range(12):
            tex_nodes[f'tex_{i}'] = nodes.new('ShaderNodeTexImage')

        mix_nodes = {}
        for i in range(12):
            mix_nodes[f'mix_{i}'] = nodes.new('ShaderNodeMixRGB')

        separate_color_nodes = {}
        for i in range(2):
            separate_color_nodes[f'separate_{i}'] = nodes.new('ShaderNodeSeparateColor')

        output.location = (796, 316)
        principled.location = (272, 308)
        normal_map.location = (-174, -804)
        tex_coord.location = (-3108, 960)
        mapping.location = (-2865, 1101)
        uv_map.location = (-2572, 379)

        tex_positions = [
            (-2050, 2074), (-2050, 1004), (-2050, -656), (-2050, 515),
            (-1600, 80), (-1600, -238), (-1250, -368), (-900, -505),
            (-1600, 1844), (-1600, 1546), (-1250, 1403), (-900, 1283)
        ]
        for i, pos in enumerate(tex_positions):
            tex_nodes[f'tex_{i}'].location = pos

        mix_positions = [
            (-1075, 2163), (-770, 1979), (-400, 1643), (-400, -1241),
            (-1075, -874), (-770, -1057), (-1075, 896), (-770, 712),
            (-400, 528), (-1075, 423), (-770, 239), (-400, 55)
        ]
        for i, pos in enumerate(mix_positions):
            mix_nodes[f'mix_{i}'].location = pos

        separate_color_nodes['separate_0'].location = (-1350, 2170)
        separate_color_nodes['separate_1'].location = (-1404, -840)
        
        links.new(tex_nodes['tex_0'].outputs['Color'], separate_color_nodes['separate_0'].inputs['Color'])
        links.new(tex_nodes['tex_2'].outputs['Color'], separate_color_nodes['separate_1'].inputs['Color'])

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        for i in range(12):
            if i < 4:
                links.new(uv_map.outputs['UV'], tex_nodes[f'tex_{i}'].inputs['Vector'])
            else:
                links.new(mapping.outputs['Vector'], tex_nodes[f'tex_{i}'].inputs['Vector'])

        # Albedo
        links.new(separate_color_nodes['separate_0'].outputs['Red'], mix_nodes['mix_0'].inputs['Fac'])
        links.new(tex_nodes['tex_9'].outputs['Color'], mix_nodes['mix_0'].inputs[1])
        links.new(tex_nodes['tex_8'].outputs['Color'], mix_nodes['mix_0'].inputs[2])

        links.new(separate_color_nodes['separate_0'].outputs['Green'], mix_nodes['mix_1'].inputs['Fac'])
        links.new(mix_nodes['mix_0'].outputs['Color'], mix_nodes['mix_1'].inputs[1])
        links.new(tex_nodes['tex_10'].outputs['Color'], mix_nodes['mix_1'].inputs[2])

        links.new(separate_color_nodes['separate_0'].outputs['Blue'], mix_nodes['mix_2'].inputs['Fac'])
        links.new(mix_nodes['mix_1'].outputs['Color'], mix_nodes['mix_2'].inputs[1])
        links.new(tex_nodes['tex_11'].outputs['Color'], mix_nodes['mix_2'].inputs[2])

        links.new(mix_nodes['mix_2'].outputs['Color'], principled.inputs['Base Color'])

        # Metallic
        links.new(tex_nodes['tex_1'].outputs['Color'], mix_nodes['mix_6'].inputs['Fac'])
        links.new(tex_nodes['tex_9'].outputs['Alpha'], mix_nodes['mix_6'].inputs[1])
        links.new(tex_nodes['tex_8'].outputs['Alpha'], mix_nodes['mix_6'].inputs[2])

        links.new(tex_nodes['tex_1'].outputs['Color'], mix_nodes['mix_7'].inputs['Fac'])
        links.new(mix_nodes['mix_6'].outputs['Color'], mix_nodes['mix_7'].inputs[1])
        links.new(tex_nodes['tex_10'].outputs['Alpha'], mix_nodes['mix_7'].inputs[2])

        links.new(tex_nodes['tex_1'].outputs['Color'], mix_nodes['mix_8'].inputs['Fac'])
        links.new(mix_nodes['mix_7'].outputs['Color'], mix_nodes['mix_8'].inputs[1])
        links.new(tex_nodes['tex_11'].outputs['Alpha'], mix_nodes['mix_8'].inputs[2])

        links.new(mix_nodes['mix_8'].outputs['Color'], principled.inputs['Metallic'])

        # Roughness
        links.new(tex_nodes['tex_3'].outputs['Color'], mix_nodes['mix_9'].inputs['Fac'])
        links.new(tex_nodes['tex_4'].outputs['Alpha'], mix_nodes['mix_9'].inputs[1])
        links.new(tex_nodes['tex_5'].outputs['Alpha'], mix_nodes['mix_9'].inputs[2])

        links.new(tex_nodes['tex_3'].outputs['Color'], mix_nodes['mix_10'].inputs['Fac'])
        links.new(mix_nodes['mix_9'].outputs['Color'], mix_nodes['mix_10'].inputs[1])
        links.new(tex_nodes['tex_6'].outputs['Alpha'], mix_nodes['mix_10'].inputs[2])

        links.new(tex_nodes['tex_3'].outputs['Color'], mix_nodes['mix_11'].inputs['Fac'])
        links.new(mix_nodes['mix_10'].outputs['Color'], mix_nodes['mix_11'].inputs[1])
        links.new(tex_nodes['tex_7'].outputs['Alpha'], mix_nodes['mix_11'].inputs[2])

        links.new(mix_nodes['mix_11'].outputs['Color'], principled.inputs['Roughness'])

        # Normal Map
        links.new(separate_color_nodes['separate_1'].outputs['Red'], mix_nodes['mix_4'].inputs['Fac'])
        links.new(tex_nodes['tex_4'].outputs['Color'], mix_nodes['mix_4'].inputs[1])
        links.new(tex_nodes['tex_5'].outputs['Color'], mix_nodes['mix_4'].inputs[2])

        links.new(separate_color_nodes['separate_1'].outputs['Green'], mix_nodes['mix_5'].inputs['Fac'])
        links.new(mix_nodes['mix_4'].outputs['Color'], mix_nodes['mix_5'].inputs[1])
        links.new(tex_nodes['tex_6'].outputs['Color'], mix_nodes['mix_5'].inputs[2])

        links.new(separate_color_nodes['separate_1'].outputs['Blue'], mix_nodes['mix_3'].inputs['Fac'])
        links.new(mix_nodes['mix_5'].outputs['Color'], mix_nodes['mix_3'].inputs[1])
        links.new(tex_nodes['tex_7'].outputs['Color'], mix_nodes['mix_3'].inputs[2])

        links.new(mix_nodes['mix_3'].outputs['Color'], normal_map.inputs['Color'])

        normal_map.inputs['Strength'].default_value = 0.5

        texture_properties = context.scene.texture_properties
        default_textures = [
            "Albedo.tga", "Metallic.tga", "Normal Map.tga", "Roughness.tga",
            "", "", "", "", "", "", "", ""
        ]

        for i in range(12):
            if i < 4:
                path = TextureProperties.get_object_texture_path(default_textures[i])
            elif i < 8:
                orig_index = i + 4
                orig_path = getattr(texture_properties, f"texture_{orig_index + 1}", "")
                if orig_path:
                    dir_path, file_name = os.path.split(orig_path)
                    new_file_name = file_name[:-5] + 'n' + file_name[-4:]
                    path = os.path.join(dir_path, new_file_name)
            else:
                path = getattr(texture_properties, f"texture_{i + 1}", "")
            
            if path:
                abs_path = self.get_absolute_path(path)
                self.report({'INFO'}, f"Trying to load texture {i+1} from: {abs_path}")
                
                if os.path.exists(abs_path):
                    try:
                        img = bpy.data.images.load(abs_path)
                        tex_nodes[f'tex_{i}'].image = img
                        self.report({'INFO'}, f"Successfully loaded texture {i+1}")
                    except Exception as e:
                        self.report({'WARNING'}, f"Couldn't load image: {abs_path}. Error: {str(e)}")
                else:
                    self.report({'WARNING'}, f"File does not exist: {abs_path}")
            else:
                self.report({'INFO'}, f"No path specified for texture {i+1}")

        mapping.inputs['Scale'].default_value = (texture_properties.tile_scale,) * 3
        
        if context.active_object:
            if context.active_object.data.materials:
                context.active_object.data.materials[0] = material
            else:
                context.active_object.data.materials.append(material)
                
        self.report({'INFO'}, f"Material created and applied")
        return {'FINISHED'}

class MaterialCreatorPanel(Panel):
    bl_label = "Material Creator"
    bl_idname = "OBJECT_PT_material_creator"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        texture_properties = context.scene.texture_properties

        layout.prop(texture_properties, "texture_9", text="Tile0_a")
        layout.prop(texture_properties, "texture_10", text="Tile1_a")
        layout.prop(texture_properties, "texture_11", text="Tile2_a")
        layout.prop(texture_properties, "texture_12", text="Tile3_a")
        
        layout.prop(texture_properties, "tile_scale")

        layout.operator(CreateMaterial.bl_idname)


def register():
    bpy.utils.register_class(TextureProperties)
    bpy.types.Scene.texture_properties = PointerProperty(type=TextureProperties)
    bpy.utils.register_class(CreateMaterial)
    bpy.utils.register_class(MaterialCreatorPanel)

def unregister():
    bpy.utils.unregister_class(CreateMaterial)
    bpy.utils.unregister_class(MaterialCreatorPanel)
    del bpy.types.Scene.texture_properties
    bpy.utils.unregister_class(TextureProperties)

if __name__ == "__main__":
    register()