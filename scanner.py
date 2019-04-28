import array
import csv
import os
import time
import bpy
import mathutils
from math import radians
from mathutils import Quaternion
from mathutils.bvhtree import BVHTree
from mathutils import Vector
import string
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
import numpy as np
import datetime
from math import pow
from math import sqrt
import sys



SCAN_HEIGHT = 256
SCAN_WIDTH = 532


def load(filepath):

    csvpath = filepath.replace('.obj', '_ModelPlacementInformation.csv')

    # Coordinate setup

    ## WoW coordinate sytem
    # Max Size: 51200 / 3 = 17066,66666666667
    # Map Size: Max Size * 2 = 34133,33333333333
    # ADT Size: Map Size / 64 = 533,3333333333333

    max_size = 51200 / 3
    map_size = max_size * 2
    adt_size = map_size / 64

    base_folder, adtname = os.path.split(filepath)
    adtsplit = adtname.split("_")
    mapname = adtsplit[0]
    map_x = int(adtsplit[1])
    map_y = int(adtsplit[2].replace(".obj", ""))

    #print(mapname)
    #print(map_x)
    #print(map_y)

    offset_x = adt_size * map_x
    offset_y = adt_size * map_y

    #print(offset_x)
    #print(offset_y)

    # Import ADT
    bpy.ops.import_scene.obj(filepath=filepath)
    bpy.context.selected_objects[0].name = mapname + '_' + str(map_x) + '_' + str(map_y)
    bpy.context.selected_objects[0].data.name = mapname + '_' + str(map_x) + '_' + str(map_y)

    bpy.ops.object.add(type='EMPTY')
    doodadparent = bpy.context.active_object
    
    doodadparent.parent = bpy.data.objects[mapname + '_' + str(map_x) + '_' + str(map_y)]
    doodadparent.name = "Doodads"
    doodadparent.rotation_euler = [0, 0, 0]
    doodadparent.rotation_euler.x = radians(-90)

    bpy.ops.object.add(type='EMPTY')
    wmoparent = bpy.context.active_object
    wmoparent.parent = bpy.data.objects[mapname + '_' + str(map_x) + '_' + str(map_y)]
    wmoparent.name = "WMOs"
    wmoparent.rotation_euler = [0, 0, 0]
    wmoparent.rotation_euler.x = radians(-90)
    # Make object active
    # bpy.context.scene.objects.active = obj

    # Read doodad definitions file
    with open(csvpath) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            doodad_path, doodad_filename = os.path.split(filepath)
            newpath = os.path.join(doodad_path, row['ModelFile'])

            if row['Type'] == 'wmo':
                bpy.ops.object.add(type='EMPTY')
                parent = bpy.context.active_object
                parent.name = row['ModelFile']
                parent.parent = wmoparent
                parent.location = (17066 - float(row['PositionX']), (17066 - float(row['PositionZ'])) * -1, float(row['PositionY']))
                parent.rotation_euler = [0, 0, 0]
                #obj.rotation_euler.x += (radians(90 + float(row['RotationX']))) # TODO
                #obj.rotation_euler.y -= radians(float(row['RotationY']))        # TODO
                parent.rotation_euler.z = radians((-90 + float(row['RotationY'])))
                if row['ScaleFactor']:
                    parent.scale = (float(row['ScaleFactor']), float(row['ScaleFactor']), float(row['ScaleFactor']))

                bpy.ops.import_scene.obj(filepath=newpath)
                obj_objects = bpy.context.selected_objects[:]

                # Put ADT rotations in here
                for obj in obj_objects:
                    obj.parent = parent

                wmocsvpath = newpath.replace('.obj', '_ModelPlacementInformation.csv')
                # Read WMO doodads definitions file
                with open(wmocsvpath) as wmocsvfile:
                    wmoreader = csv.DictReader(wmocsvfile, delimiter=';')
                    for wmorow in wmoreader:
                        wmodoodad_path, wmodoodad_filename = os.path.split(filepath)
                        wmonewpath = os.path.join(wmodoodad_path, wmorow['ModelFile'])
                        # Import the doodad
                        if(os.path.exists(wmonewpath)):
                            bpy.ops.import_scene.obj(filepath=wmonewpath)
                            # Select the imported doodad
                            wmoobj_objects = bpy.context.selected_objects[:]
                            for wmoobj in wmoobj_objects:
                                # Prepend name
                                wmoobj.name = "(" + wmorow['DoodadSet'] + ") " + wmoobj.name
                                # Set parent
                                wmoobj.parent = parent
                                # Set position
                                wmoobj.location = (float(wmorow['PositionX']) * -1, float(wmorow['PositionY']) * -1, float(wmorow['PositionZ']))
                                # Set rotation
                                rotQuat = Quaternion((float(wmorow['RotationW']), float(wmorow['RotationX']), float(wmorow['RotationY']), float(wmorow['RotationZ'])))
                                rotEul = rotQuat.to_euler()
                                rotEul.x += radians(90);
                                rotEul.z += radians(180);
                                wmoobj.rotation_euler = rotEul
                                # Set scale
                                if wmorow['ScaleFactor']:
                                    wmoobj.scale = (float(wmorow['ScaleFactor']), float(wmorow['ScaleFactor']), float(wmorow['ScaleFactor']))

                                # Duplicate material removal script by Kruithne
                                # Merge all duplicate materials
                                # for obj in bpy.context.scene.objects:
                                #     if obj.type == 'MESH':
                                #         i = 0
                                #         for mat_slot in obj.material_slots:
                                #             mat = mat_slot.material
                                #             obj.material_slots[i].material = bpy.data.materials[mat.name.split('.')[0]]
                                #             i += 1

                                # # Cleanup unused materials
                                # for img in bpy.data.images:
                                #     if not img.users:
                                #         bpy.data.images.remove(img)
            else:
                if(os.path.exists(newpath)):
                    bpy.ops.import_scene.obj(filepath=newpath)
                    obj_objects = bpy.context.selected_objects[:]
                    for obj in obj_objects:
                        # Set parent
                        obj.parent = doodadparent

                        # Set location
                        obj.location.x = (17066 - float(row['PositionX']))
                        obj.location.y = (17066 - float(row['PositionZ'])) * -1
                        obj.location.z = float(row['PositionY'])
                        obj.rotation_euler.x += radians(float(row['RotationZ']))
                        obj.rotation_euler.y += radians(float(row['RotationX']))
                        obj.rotation_euler.z = radians(90 + float(row['RotationY'])) # okay

                        # Set scale
                        if row['ScaleFactor']:
                            obj.scale = (float(row['ScaleFactor']), float(row['ScaleFactor']), float(row['ScaleFactor']))


    # Set doodad and WMO parent to 0
    wmoparent.location = (0, 0, 0)
    doodadparent.location = (0, 0, 0)

    print("Deduplicating and cleaning up materials!")
    # Duplicate material removal script by Kruithne
    # Merge all duplicate materials
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            i = 0
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                obj.material_slots[i].material = bpy.data.materials[mat.name.split('.')[0]]
                i += 1

    # Cleanup unused materials
    for img in bpy.data.images:
        if not img.users:
            bpy.data.images.remove(img)
    
    return mapname + '_' + str(map_x) + '_' + str(map_y)

def grid_init(scale, x_size, y_size):
     #Lowhigh setup
    lh_start_z = -SCAN_HEIGHT / 2
    lh_start_x = -SCAN_WIDTH / 2
    lh_start_y = SCAN_WIDTH / 2
    
    bpy.ops.object.add(type='EMPTY')
    bpy.context.selected_objects[0].name = "scanplane"
    scanplane = bpy.context.selected_objects[0]
    scanplane.location = (lh_start_x, lh_start_y, lh_start_z)
    
    source_dsts = []
    
    for x in range(x_size):

        dsts_line = []
        for y in range(y_size): 
            location = (scanplane.location.x + x * scale,  scanplane.location.y - y * scale, scanplane.location.z)          
            dsts_line.append(location)        
        source_dsts.append(dsts_line)
        
    bpy.ops.object.delete()
        
    return source_dsts
    
def cast_ray(src, dst, scale):
    scene = bpy.context.scene
    return scene.ray_cast(src, dst, distance = scale)

def side_scan(fro, side_grid, scale, rev=False):
    
    if rev == False:
        for z in range(fro): 
            hits = []
            for sccube in side_grid[0]:
                x_plus_dst = [sccube[0] + scale / 2, sccube[1], sccube[2] + z * scale]
                caster = [sccube[0] / 2, sccube[1], sccube[2] + z * scale]
                hits.append(cast_ray(caster, x_plus_dst, scale)[0])
            if True in hits:
                hitted = True
                return z
    else:
        for z in reversed(range(fro)): 
            hits = []
            for sccube in side_grid[0]:
                x_plus_dst = [sccube[0] + scale / 2, sccube[1], sccube[2] + z * scale]
                caster = [sccube[0] / 2, sccube[1], sccube[2] + z * scale]
                hits.append(cast_ray(caster, x_plus_dst, scale)[0])
            if True in hits:
                hitted = True
                return z
            
def join_map():
    scene = bpy.context.scene
    
    print("Joining meshes")
    bpy.ops.object.select_all(action='DESELECT')
    obs = []
    for ob in scene.objects:
        if ob.type == 'MESH':
            obs.append(ob)
    ctx = bpy.context.copy()
    ctx['active_object'] = obs[0]
    ctx['selected_objects'] = obs
    ctx['selected_editable_bases'] = [scene.object_bases[ob.name] for ob in obs]
    bpy.ops.object.join(ctx) # <-- Here it gets stucked 
            
def scanmap(mapname):
    
    print("Initializing " + mapname + " " + str(datetime.datetime.now().time()))
    scale = 1
    matrix = np.zeros((SCAN_WIDTH, SCAN_WIDTH, SCAN_HEIGHT), dtype = int)
    
    ###########################################################################
    join_map() # <--- Problematic area
    ###########################################################################
    
    scene = bpy.context.scene
    print("Creating grid")
    source_dsts = grid_init(scale, SCAN_WIDTH, SCAN_WIDTH)
    
    print("Initializing tree")
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            objt = obj
            tree = BVHTree.FromObject(obj, scene)
        
    print("Starting scan of " + mapname + ": " + str(datetime.datetime.now().time()))
    for z in range(SCAN_HEIGHT): # Posun na Z
        for idxx, line in enumerate(source_dsts):
            for idxy, sccube in enumerate(line):
                H_1 = [sccube[0], sccube[2] + z * scale, sccube[1]]
                v = Vector(list(H_1))
                matc = 1
                
                loc, norm, polid, dist = tree.find_nearest(v)
                pog = objt.data.polygons[polid]
                slot = objt.material_slots[pog.material_index]
                mat = slot.material
                if mat is not None:
                    matc = mat.diffuse_color
                if dist <= 0.9:
                    matrix[idxy][idxx][z] = matc
                #print("Pt " + str(idxx) + " " + str(idxy) + " completed at " + str(datetime.datetime.now().time()))
            #print("Line " + str(idxx) + " completed at " + str(datetime.datetime.now().time()))
                                   
        print("Map " + mapname + " layer completed: " + str(z) + " at " + str(datetime.datetime.now().time()))

    filename = 'export_mat_' + mapname
    print("Writing to file" + filename)
    with open(filename, 'a') as f:
        for z in range(SCAN_HEIGHT):
            f.write('\n')
            f.write('Layer: ' + str(z))
            for x in range(SCAN_WIDTH):
                f.write('\n')
                for y in range(SCAN_WIDTH):
                    f.write(str(matrix[y][x][z]))             
    
    print(mapname + " DONE")
    
#########################################################################################
    
    
path = r"D:\WOWTOMINECRAFT\Exports\world\maps\azeroth\azeroth_32_49.obj"
mname = load(path) # <-- Script for loading map tiles, not made by me

bpy.data.objects[mname].select = True
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
obj = bpy.data.objects[mname]
obj.location.x = 0
obj.location.y = 0
obj.location.z = 0

scanmap((path.split("\\")[-1:])[0])

