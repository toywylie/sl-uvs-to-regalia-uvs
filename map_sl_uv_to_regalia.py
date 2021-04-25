import bpy
import urllib
import shutil
import os.path

# path to the SL body textures that should be converted
SOURCE_UPPER_BODY_IMAGE = bpy.path.abspath('//sl_upper_body_template.png')
SOURCE_LOWER_BODY_IMAGE = bpy.path.abspath('//sl_lower_body_template.png')

# path to the Regalia Development Kit blend files 1.7 and 1.8
REGALIA_BLEND_FILE_17 = bpy.path.abspath('//Project_Regalia_furrybody_MASTER_1.7.blend')
REGALIA_BLEND_FILE_18 = bpy.path.abspath('//Project_Regalia_furrybody_DUMMY_1.8experimental.blend')
# path to the SL body DAE file
SL_BODY_DAE_FILE = bpy.path.abspath('//SL_Female_Body_UV_Mod.dae')
# URL to download the SL bod DAE file
SL_BODY_DAE_DOWNLOAD = 'https://raw.githubusercontent.com/toywylie/sl-uvs-to-regalia-uvs/master/SL_Female_Body_UV_Mod.dae'

# creates a new emissive material in the object, adding the image as texture input
def create_emissive_material(object, material_name, image):
    # Create new materials for the object
    material = bpy.data.materials.new(name = material_name)
    material.use_nodes = True

    # Clear out nodes on the material that were atomatically created
    nodes = material.node_tree.nodes
    nodes.clear()

    # Add new emissive material setup
    texture = nodes.new(type = 'ShaderNodeTexImage')
    emission_shader = nodes.new(type = 'ShaderNodeEmission')
    material_output = nodes.new(type = 'ShaderNodeOutputMaterial')

    texture.image = image

    links = material.node_tree.links
    link = links.new(emission_shader.outputs[0],material_output.inputs[0])
    link = links.new(texture.outputs[0],emission_shader.inputs[0])

    # Add new materials to the object
    object.data.materials.append(material)

    return material

#
# Clean up the scene
#

# Make sure we are in Object mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode = 'OBJECT')

# Select everything and delete, to start fresh
bpy.ops.object.select_all(action = 'SELECT')
bpy.ops.object.delete(use_global = True)

# In case any objects were missed, delete them directly from the data
while len(bpy.data.objects):
    bpy.data.objects.remove(bpy.data.objects[0])

# Cleanup orphaned data blocks
while bpy.ops.outliner.orphans_purge() != {'CANCELLED'}:
    pass

#
# Load meshes from external sources
#

# Check if source images are available
if not os.path.isfile(SOURCE_LOWER_BODY_IMAGE):
    raise Exception()
if not os.path.isfile(SOURCE_UPPER_BODY_IMAGE):
    raise Exception()

# Check if the Regalia dev kit is available
devkit_file = REGALIA_BLEND_FILE_18
if not os.path.isfile(REGALIA_BLEND_FILE_18):
    devkit_file = REGALIA_BLEND_FILE_17
    if not os.path.isfile(REGALIA_BLEND_FILE_17):
        raise Exception()

# Check if SL body DAE needs to be downloaded
if not os.path.isfile(SL_BODY_DAE_FILE):
    with urllib.request.urlopen(SL_BODY_DAE_DOWNLOAD) as response, open(SL_BODY_DAE_FILE, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

# Check if SL body DAE is now available
if not os.path.isfile(SL_BODY_DAE_FILE):
    raise Exception()

# Append the Regalia main body
bpy.ops.wm.append(
    directory = devkit_file + '/Object',
    filename = 'body_athletic'
)

# Prepare variables
regalia_armature = None

# Find main body and armature (don't rely on names just in case they change in the future)
for object in bpy.data.objects:
    if object.type == 'ARMATURE':
        regalia_armature = object
    elif object.type == 'MESH':
        regalia_body = object

# Bail out if something is missing
if regalia_armature == None:
    raise Exception()

# Append the rest of the body
# Parts available in one devkit but not the other will fail silently, so we
# just load all of them

# 1.7 devkit
bpy.ops.wm.append(
    directory = devkit_file + '/Object',
    filename = 'athletic_wrists'
)

# 1.7 devkit
bpy.ops.wm.append(
    directory = devkit_file + '/Object',
    filename = 'athletic_hands'
)

# 1.8 devkit
bpy.ops.wm.append(
    directory = devkit_file + '/Object',
    filename = 'HANDS'
)

# 1.7 and 1.8 devkit
bpy.ops.wm.append(
    directory = devkit_file + '/Object',
    filename = 'planti-feet_athletic'
)

# Import SL body DAE file
bpy.ops.wm.collada_import(filepath = SL_BODY_DAE_FILE)

#
# Clean up scene to reduce clutter and make parsing easier
#

# Prepare variable
base_female_body = None

# Prepare list of objects to remove, like armature custom bone shapes
to_delete = []

# Go through all objects in the scene
for object in bpy.data.objects:

    # Mark all unparented meshes for deletion (this will catch the custom bone shapes)
    if object.parent == None and object.type == 'MESH':
        # Remember object pointers to the SL standard body
        to_delete.append(object)

    else:
        # Make sure to unhide every object found
        object.hide_viewport = False

        if object.type == 'MESH':
            # Reparent all found meshes to the Regalia armature
            object.parent = regalia_armature

            # Remember object pointer to the SL standard body
            if object.name == 'SL Female Body':
                base_female_body = object

            # Go through all modifiers of the discovered objects
            for modifier in object.modifiers:
                # Make sure the armature modifiers point to the Regalia armature
                if modifier.type == 'ARMATURE':
                    modifier.object = regalia_armature

        # Any non-mesh objects that are not the Regalia armature need to be deleted
        elif object != regalia_armature:
            to_delete.append(object)

# Bail out if something is missing
if base_female_body == None:
    raise Exception()

# Delete the objects found above
for object in to_delete:
    bpy.data.objects.remove(object)

#
# Join Regalia body parts into one
#

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

# Select all available Regalia body parts
for part in ['athletic_hands', 'athletic_wrists', 'planti-feet_athletic', 'body_athletic', 'HANDS']:
    if part in bpy.data.objects:
        bpy.data.objects[part].select_set(True)

# Make the main body the active object
bpy.context.view_layer.objects.active = bpy.data.objects['body_athletic']

# Join everything
bpy.ops.object.join()

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

# Find the new joined Regalia body
regalia_body = bpy.data.objects['body_athletic']

# bail out if the body is missing
if regalia_body == None:
    raise Exception()

#
# Reduce materials on the Regalia Body to 2: Left and Right
#

# Make sure the body is selected
regalia_body.select_set(True)

# Remove all unused material slots
bpy.ops.object.material_slot_remove_unused()

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

# Add baking images
bake_left_image = bpy.data.images.new(name = "Regalia Bake Left",width=2048,height=2048)
bake_right_image = bpy.data.images.new(name = "Regalia Bake Right",width=2048,height=2048)

# Add two new materials, one for each half of the body
material_regalia_left = create_emissive_material(regalia_body, "Regalia Left", bake_left_image)
material_regalia_right = create_emissive_material(regalia_body, "Regalia Right", bake_right_image)

# Go into edit mode
bpy.ops.object.editmode_toggle()

# Go into face select mode
bpy.ops.mesh.select_mode(type = 'FACE')

# Deselect everything, just in case
bpy.ops.mesh.select_all(action = 'DESELECT')

# Select all faces on the right side of the body, based on the materials
slot_index = 0
for slot in regalia_body.material_slots:
    if slot.name in ["a", "b", "c", "n"] or slot.name[:2] in ["a.", "b.", "c.", "d."]:
        regalia_body.active_material_index = slot_index
        bpy.ops.object.material_slot_select()
    slot_index += 1

# Assign all faces on the right to the new material
regalia_body.active_material = material_regalia_right
bpy.ops.object.material_slot_assign()

# Deselect everything
bpy.ops.mesh.select_all(action = 'DESELECT')

# Invert selection (doesn't work, the material flips to left when set to active)
# bpy.ops.mesh.select_all(action = 'INVERT')

# Select all faces on the left side of the body, based on the materials
slot_index = 0
for slot in regalia_body.material_slots:
    if slot.name == "o" or slot.name[:2] in ["e.", "f.", "g.", "h."]:
        regalia_body.active_material_index = slot_index
        bpy.ops.object.material_slot_select()
    slot_index += 1

# Assign all faces on the left to the new material
regalia_body.active_material = material_regalia_left
bpy.ops.object.material_slot_assign()

# Exit edit mode
bpy.ops.object.editmode_toggle()

# Clear unused materials
bpy.ops.object.material_slot_remove_unused()

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

#
# Prepare SL body
#

# Align SL body to Regalia rig
base_female_body.rotation_euler.z -= 3.14159 / 2.0

# Load source images
sl_skin_upper_image = bpy.data.images.load(SOURCE_UPPER_BODY_IMAGE)
sl_skin_lower_image = bpy.data.images.load(SOURCE_LOWER_BODY_IMAGE)

sl_upper_emissive = create_emissive_material(base_female_body, "SL Upper Body", sl_skin_upper_image)
sl_lower_emissive = create_emissive_material(base_female_body, "SL Lower Body", sl_skin_lower_image)

# Apply rotational transform
bpy.ops.object.transform_apply(rotation=True)

#
# Set up materials for SL body
#

# Select the SL body and bring it into edit mode
base_female_body.select_set(True)
bpy.context.view_layer.objects.active = base_female_body
bpy.ops.object.editmode_toggle()

# Go into face select mode
bpy.ops.mesh.select_mode(type = 'FACE')

# Deselect everything just to be safe
bpy.ops.mesh.select_all(action = 'DESELECT')

# Reassign upper body material
base_female_body.active_material_index = 0
bpy.ops.object.material_slot_select()
base_female_body.active_material = sl_upper_emissive
bpy.ops.object.material_slot_assign()

# Deselect everything
bpy.ops.mesh.select_all(action = 'DESELECT')

# Reassign lower body material
base_female_body.active_material_index = 1
bpy.ops.object.material_slot_select()
base_female_body.active_material = sl_lower_emissive
bpy.ops.object.material_slot_assign()

# Switch back to object mode
bpy.ops.object.editmode_toggle()

# Clear unused materials
base_female_body.select_set(True)
bpy.ops.object.material_slot_remove_unused()

#
# Set up Shrinkwrap modifier
#

shrinkwrap = base_female_body.modifiers.new(name = "Shrinkwrap", type = "SHRINKWRAP")
shrinkwrap.target = regalia_body
shrinkwrap.offset = 0.001
shrinkwrap.wrap_method = 'NEAREST_SURFACEPOINT'
shrinkwrap.wrap_mode = 'OUTSIDE_SURFACE'

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

#
# Pose Avatar
#

regalia_armature.select_set(True)
bpy.ops.object.posemode_toggle()

regalia_armature.pose.bones['HipLeft'].rotation_mode = 'XYZ'
regalia_armature.pose.bones['HipRight'].rotation_mode = 'XYZ'
regalia_armature.pose.bones['HipLeft'].rotation_euler[2] = -3.1415 / 4.0
regalia_armature.pose.bones['HipRight'].rotation_euler[2] = 3.1415 / 4.0

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

#
# Apply modifiers, this makes baking work better
#

# Apply armature to Regalia body
regalia_body.select_set(True)
bpy.context.view_layer.objects.active = regalia_body
bpy.ops.object.modifier_apply(modifier = "Avatar")
regalia_body.select_set(False)

# Apply armature and shrinkwrap to SL body
base_female_body.select_set(True)
bpy.context.view_layer.objects.active = base_female_body
bpy.ops.object.modifier_apply(modifier = "Armature")
bpy.ops.object.modifier_apply(modifier = "Shrinkwrap")
base_female_body.select_set(False)

regalia_body.parent = None
base_female_body.parent = None

regalia_armature.select_set(True)
bpy.ops.object.delete(use_global=False)

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

#
# Set up rendering
#

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 1
bpy.context.scene.cycles.preview_samples = 1

bpy.context.scene.render.bake.use_selected_to_active = True
bpy.context.scene.render.bake.cage_extrusion = 0.05

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

base_female_body.select_set(True)
regalia_body.select_set(True)

# Make the Regalia body the active object
bpy.context.view_layer.objects.active = bpy.data.objects['body_athletic']

regalia_body.show_wire = False
regalia_body.show_all_edges = False

# BAKE!
bpy.ops.object.bake(type = 'EMIT')

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

#
# Show result
#

regalia_body.select_set(True)
bpy.ops.object.parent_clear()

regalia_body.location[0] += 3.0

regalia_body.show_wire = False
regalia_body.show_all_edges = False

# Deselect everything
bpy.ops.object.select_all(action = 'DESELECT')

# Save baked images
bake_left_image.filepath_raw = "//Regalia_Bake_Left.png"
bake_left_image.file_format = 'PNG'
bake_left_image.save()

bake_right_image.filepath_raw = "//Regalia_Bake_Right.png"
bake_right_image.file_format = 'PNG'
bake_right_image.save()

# Cleanup orphaned data blocks
while bpy.ops.outliner.orphans_purge() != {'CANCELLED'}:
    pass
