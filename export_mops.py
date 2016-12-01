import bpy
import os
import operator
from  mathutils import *
import math
from struct import pack

SIZE_OBJECTINFO = 64
SIZE_ARGB = 4
SIZE_QUAT = 16
SIZE_VECTOR = 12
SIZE_POINT = 12
SIZE_VERTEX = 10
SIZE_TRIANGLE = 8
SIZE_MATERIAL = 212
SIZE_BONE = 160
SIZE_INFLUENCE = 12
SIZE_ANIMATION = 76
SIZE_ANIMBONE = 68
SIZE_ANIMKEY = 32


class ObjectMap( object ):
    
    def __init__( self ):
        self.dict = {}
        self.index = 0
    
    def get( self, obj ):
        if obj in self.dict:
            return self.dict[ obj ]
        else:
            ret_index = self.index
            self.dict[ obj ] = ret_index
            self.index += 1
            return ret_index
    
    def items( self ):
        get_value = operator.itemgetter( 0 )
        get_key = operator.itemgetter( 1 )
        return map( get_value, sorted( self.dict.items(), key = get_key ) )
            

class ObjectInfo( object ):
    
    def __init__( self, name ):
        self.name = name

    def dump( self ):
        return pack( '<64s', str.encode( self.name ) )
    

class ARGB( object ):
    
    def __init__( self, a = 255, r = 0, g = 0, b = 0 ):
        self.a = a
        self.r = r
        self.g = g
        self.b = b
        
    def dump( self ):
        return pack( '<4B', self.b, self.g, self.r, self.a )


class Quat( object ):
    
    def __init__( self ):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.w = 0.0
        
    def dump( self ):
        return pack( '<4f', self.x, self.z, self.y, self.w )
    
    def __str__( self ):
        return "<Quaternion x:%.3f, y:%.3f, z:%.3f, w:%.3f>" % ( self.x, self.y, self.z, self.w )
    
    def _val( self ):
        return ( type( self ).__name__, self.x, self.y, self. z, self.w )
    
    def __neg__( self ):
        q = Quat()
        q.x = -self.x
        q.y = -self.y
        q.z = -self.z
        q.w = self.w
        return q
    
    def __mul__( self, other ):
        q = Quat()
        q.w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        q.x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        q.y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        q.z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return q
    
    def __eq__( self, other ):
        if not hasattr( other, "_val" ):
            return False
        return self._val() == other._val()


class Vector( object ):
    
    def __init__( self, x = 0.0, y = 0.0, z = 0.0 ):
        self.x = x
        self.y = y
        self.z = z
        
    def dump( self ):
        return pack( '<3f', self.x, self.z, self.y )
    
    def __str__( self ):
        return "<Vector x:%.3f, y:%.3f, z:%.3f>" % ( self.x, self.y, self.z )
    
    def _val( self ):
        return ( type( self ).__name__, self.x, self.y, self.z )
    
    def __eq__( self, other ):
        if not hasattr( other, "_val" ):
           return False
        return self._val() == other._val()
        
    def dot( self, vector ):
        return self.x * vector.x + self.y * vector.y + self.z * vector.z
    
    def cross( self, vector ):
        return Vector( self.y * vector.z - self.z * vector.y, self.z * vector.x - self.x * vector.z, self.x * vector.y - self.y * vector.x )
    
    def __sub__( self, other ):
        return Vector( self.x - other.x, self.y - other.y, self.z - other.z )


class Point( object ):
    
    def __init__( self ):
        self.point = Vector()
    
    def dump( self ):
        return self.point.dump()
    
    def __str__( self ):
        return "<Point \ncoords:{}>".format( self.point )
    
    def _val( self ):
        return ( type( self ).__name__, self.point._val() )
    
    def __eq__( self, other ):
        if not hasattr( other, "_val" ):
            return False
        return self._val() == other._val()
    
    def __hash__( self ):
        return hash( self._val() )

    
class Vertex( object ):
    
    def __init__( self ):
        self.point_index = 0
        self.u = 0.0
        self.v = 0.0
        self.material_index = 0
    
    def dump( self ):
        return pack('<Hff', self.point_index, self.u, self.v )
    
    def _val( self ):
        return ( type( self ).__name__, self.point_index, self.u, self.v, self.material_index )
    
    def __eq__( self, other ):
        if not hasattr( other, "_val" ):
            return False
        return self._val() == other._val()
    
    def __hash__( self ):
        return hash( self._val() )


class Triangle( object ):
    
    def __init__( self ):
        self.index1 = 0
        self.index2 = 0
        self.index3 = 0
        self.material_index = 0
    
    def dump( self ):
        return pack( 'HHHH', self.index1, self.index2, self.index3, self.material_index )
    
    def __lt__( self, other ):
        return self.material_index < other.material_index


class Material( object ):
    
    def __init__( self ):
        self.material_name = ""
        self.texture_name = ""
        self.texture_source = ""
        self.ambient = ARGB()
        self.diffuse = ARGB()
        self.specular = ARGB()
        self.emmissive = ARGB()
        self.power = 1.0
        
    def dump( self ):
        data = pack( '<64s64s64s', str.encode( self.material_name ), str.encode( self.texture_name ), str.encode( self.texture_source ) )
        data += self.ambient.dump() + self.diffuse.dump() + self.specular.dump() + self.emmissive.dump()
        data += pack( 'f', self.power )
        return data


class Bone( object ):
    
    def __init__( self ):
        self.name = ""
        self.parent_name = ""
        self.vertex_count = 0
        self.position = Vector()
        self.orientation = Quat()
        
    def dump( self ):
        data = pack( '<64s64s', str.encode( self.name ), str.encode( self.parent_name ) )
        data += self.position.dump() + self.orientation.dump() + pack( '<l', self.vertex_count )
        return data


class Influence( object ):
    
    def __init__( self ):
        self.bone_index = 0
        self.vertex_index = 0
        self.weight = 0.0
        
    def dump( self ):
        return pack( 'llf', self.bone_index, self.vertex_index, self.weight )
        

class Animation( object ):
    
    def __init__( self ):
        self.name = ""
        self.bone_count = 0
        self.key_count = 0
        self.track_time = 0
    
    def dump( self ):
        return pack( '<64s3l', str.encode( self.name ), self.bone_count, self.key_count, self.track_time )


class ABone( object ):
    
    def __init__( self ):
        self.name = ""
        self.key_count = 0
    
    def dump( self ):
        return pack( '<64sl', str.encode( self.name ), self.key_count )
        

class AKey( object ):
    
    def __init__( self ):
        self.position = Vector()
        self.orientation = Quat()
        self.time = 0
        
    def dump( self ):
        return self.position.dump() + self.orientation.dump() + pack( '<l', self.time )


class ChunkHeader( object ):
    
    def __init__( self, name, type_size ):
        self.chunk_id = str.encode( name )
        self.data_size = type_size
        self.data_count = 0
    
    def dump( self ):
        return pack( '<20sll', self.chunk_id, self.data_size, self.data_count )


class Chunk( object ):
    
    def __init__( self, name, type_size ):
        self.header = ChunkHeader( name, type_size )
        self.data = []
        
    def dump( self ):
        buffer = self.header.dump()
        for i in range( len( self.data ) ):
            buffer = buffer + self.data[ i ].dump()
        return buffer
    
    def update_header( self ):
        self.header.data_count = len( self.data )


class MOPSFile( object ):
    
    def __init__( self ):
        self.general_header = ChunkHeader( "Mops_in_bytes", 0 )
        self.info = Chunk( "INFO", SIZE_OBJECTINFO )
        self.points = Chunk( "PNTS", SIZE_POINT )
        self.vertices = Chunk ("VERT", SIZE_VERTEX )
        self.faces = Chunk( "FACE", SIZE_TRIANGLE )
        self.materials = Chunk( "MATT", SIZE_MATERIAL )
        self.bones = Chunk( "BONE", SIZE_BONE )
        self.influences = Chunk( "INFLUENCE", SIZE_INFLUENCE )
        self.animations = Chunk( "ANIMAT", SIZE_ANIMATION )
        self.anim_bones = Chunk( "ANIMBONE", SIZE_ANIMBONE )
        self.anim_keys = Chunk( "ANIMKEY", SIZE_ANIMKEY )
        
    def add_info( self, i ):
        self.info.data.append( i )
    
    def add_point( self, p ):
        self.points.data.append( p )
        
    def add_vertex( self, v ):
        self.vertices.data.append( v )
        
    def add_face( self, f ):
        self.faces.data.append( f )
        
    def add_material( self, m ):
        self.materials.data.append( m )
        
    def add_bone( self, b ):
        self.bones.data.append( b )
        
    def add_influence( self, inf ):
        self.influences.data.append( inf )
        
    def add_animation( self, an ):
        self.animations.data.append( an )
        
    def add_anim_bone( self, ab ):
        self.anim_bones.data.append( ab )
        
    def add_anim_key( self, k ):
        self.anim_keys.data.append( k )
        
    def update_headers( self ):
        self.info.update_header()
        self.points.update_header()
        self.vertices.update_header()
        self.faces.update_header()
        self.materials.update_header()
        self.bones.update_header()
        self.influences.update_header()
        self.animations.update_header()
        self.anim_bones.update_header()
        self.anim_keys.update_header()
    
    def dump( self ):
        self.update_headers()
        data = self.general_header.dump()
        data += self.info.dump()
        data += self.points.dump()
        data += self.vertices.dump()
        data += self.faces.dump()
        data += self.materials.dump()
        data += self.bones.dump()
        data += self.influences.dump()
        data += self.animations.dump()
        data += self.anim_bones.dump()
        data += self.anim_keys.dump()
        return data

    def print( self ):
        print( "*****" )
        print( "{:<15} {}".format( "Info", self.info.data[ 0 ].name ) )
        print( "{:<15} {}".format( "Points", len( self.points.data ) ) )
        print( "{:<15} {}".format( "Vertices", len( self.vertices.data ) ) )
        print( "{:<15} {}".format( "Faces", len( self.faces.data ) ) )
        print( "{:<15} {}".format( "Materials", len( self.materials.data ) ) )
        print( "{:<15} {}".format( "Bones", len( self.bones.data ) ) )
        print( "{:<15} {}".format( "Influences", len( self.influences.data ) ) )
        print( "{:<15} {}".format( "Animations", len( self.animations.data ) ) )
        print( "{:<15} {}".format( "Animation bones", len( self.anim_bones.data ) ) )
        print( "{:<15} {}".format( "Animation keys", len( self.anim_keys.data ) ) )
        print()


def parse_mesh_and_armature( mesh, armature, mops ):
    
    print( "Mesh parsing..." )
    
    scene = bpy.context.scene
        
    print( "Materials..." )
    print( "{:<20}{}".format( "Materials count", len( mesh.material_slots ) ) )
    
    material_slot_index = 0
    
    for material_slot in mesh.material_slots:
        material = Material()
        
        texture = material_slot.material.active_texture
        texture_name = texture.name if texture is not None else ""
        texture_source = texture.image.name if texture_name and texture.image is not None else ""
        
        material.material_name = material_slot.name
        material.texture_name = texture_name
        material.texture_source = texture_source
        
        ambient = material_slot.material.ambient * material_slot.material.diffuse_color
        diffuse = material_slot.material.diffuse_color
        specular = material_slot.material.specular_color
        
        material.ambient.r = int( 255 * ambient.r )
        material.ambient.g = int( 255 * ambient.g )
        material.ambient.b = int( 255 * ambient.b )
        
        material.diffuse.r = int( 255 * diffuse.r )
        material.diffuse.g = int( 255 * diffuse.g )
        material.diffuse.b = int( 255 * diffuse.b )
        
        material.specular.a = int( 255 * material_slot.material.specular_alpha )
        material.specular.r = int( 255 * specular.r )
        material.specular.g = int( 255 * specular.g )
        material.specular.b = int( 255 * specular.b )
        
        mops.add_material( material )
        
        print( "Material {} '{}' with texture '{}' from file '{}'".format( material_slot_index, material_slot.name, texture_name, texture_source ) )
        
        material_slot_index += 1
    
    print ("Parsing Faces..." )
        
    linked_points = {}
    points = ObjectMap()
    vertices = ObjectMap()
    triangles = []
    
    per = 0
    face_count = float( len( mesh.data.tessfaces ) )
    
    for face in mesh.data.tessfaces:
        
        has_uv = False
        uv_layer = None
        face_uv = None
        
        if len( mesh.data.uv_textures ) > 0:
            has_uv = True
            uv_layer = mesh.data.tessface_uv_textures.active
            face_uv = uv_layer.data[ face.index ]
        
        wedges = []
        vectors = []
        
        p = int( 100 * face.index / face_count )
        if p > per + 7:
            per = p
            print( "Parsing faces is completed by {}%".format( per ) )
    
        for i in range( 3 ):
            vertex_index = face.vertices[ i ]
            vertex_m = mesh.data.vertices[ vertex_index ]
            vertex_position = mesh.matrix_local * vertex_m.co
            
            point = Point()
            point.point.x = vertex_position.x
            point.point.y = vertex_position.y
            point.point.z = vertex_position.z
            point_index = points.get( point )
            
            uv = []
            if has_uv and len( face_uv.uv ) == 3:
                uv = [ face_uv.uv[ i ][ 0 ], face_uv.uv[ i ][ 1 ] ]
            else:
                uv = [ 0.0, 0.0 ]
            
            vertex = Vertex()
            vertex.point_index = point_index
            vertex.u = uv[ 0 ]
            vertex.v = uv[ 1 ]
            vertex.material_index = face.material_index
            vertex_index = vertices.get( vertex )
            
            if point in linked_points:
                if not( vertex_index in linked_points[ point ] ):
                    linked_points[ point ].append( vertex_index )
            else:
                linked_points[ point ] = [ vertex_index ]
            
            wedges.append( vertex_index )
            vectors.append( Vector( vertex_position.x, vertex_position.z, vertex_position.y ) )
            
        face_normal = Vector( face.normal[ 0 ], face.normal[ 2 ], face.normal[ 1 ] )
        normal = ( vectors[ 1 ] - vectors[ 0 ] ).cross( vectors[ 2 ] - vectors[ 1 ] )
        dot = face_normal.dot( normal )
        triangle = Triangle()
        triangle.material_index = face.material_index
        
        if dot > 0:
            ( triangle.index1, triangle.index2, triangle.index3 ) = wedges
        else:
            ( triangle.index3, triangle.index2, triangle.index1 ) = wedges
        triangles.append( triangle )
    
    triangles.sort()
    print( "Parsing faces is completed.".format( per ) )
    
    for point in points.items():
        mops.add_point( point )
    
    for vertex in vertices.items():
        mops.add_vertex( vertex )
    
    for triangle in triangles:
        mops.add_face( triangle )
    
    print( "Parsing Armature..." )
    
    vertex_groups = {}
    
    for obj_vertex_group in mesh.vertex_groups:
        v_list = []
        for vertex in mesh.data.vertices:
            for v_group in vertex.groups:
                if v_group.group == obj_vertex_group.index:
                    v_pos = mesh.matrix_local * vertex.co
                    point = Point()
                    point.point.x = v_pos.x
                    point.point.y = v_pos.y
                    point.point.z = v_pos.z
                    
                    try:
                        for vertex_index in linked_points[ point ]:
                            v_list.append( ( vertex_index, v_group.weight ) )
                    except Exception:
                        print( "Error link point {}".format( point ) )
                        pass
                    
        vertex_groups[ obj_vertex_group.name ] = v_list
    
    if armature is None:
        print( "Armature not found" )
        return
    print( armature.name )
    
    root_bones = [ b for b in armature.data.bones if b.parent is None and b.use_deform == True ]
    
    if len( root_bones ) == 0:
        raise Exception( "Cannot find root bone" )
    elif len( root_bones ) > 1:
        print( root_bones )
        raise Exception( "More then one root bone founded" )
        
    bones_list = []
    
    parse_bone( root_bones[ 0 ], bones_list, vertex_groups, mops )

    print( "Parse Animations..." )
    
    restore_action = armature.animation_data.action
    restore_frame = scene.frame_current
    fps = scene.render.fps
    
    for action in bpy.data.actions:
        
        if not len( action.fcurves ):
            print( "Has no keys..." )
            continue
            
        armature.animation_data.action = action
        scene.update()
            
        start_frame, end_frame = action.frame_range
        start_frame = int( start_frame )
        end_frame = int( end_frame ) 
        frame_range = range( start_frame, end_frame + 1 )
        frame_count = len( frame_range )

        action_bones = []
        for gr in action.groups:
            for ab in armature.pose.bones:
                if gr.name == ab.name:
                    action_bones.append( ab )
                    bone = ABone()
                    bone.name = ab.name
                    bone.key_count = frame_count
                    mops.add_anim_bone( bone )
                    
        bones_keys = {}
        for i in frame_range:
            
            scene.frame_set( i )
            
            for bone_data in action_bones:
                key = AKey()
                key.time = int( 1000.0 * i / fps )
                
                matrix = bone_data.matrix_basis.to_3x3()
                quat = matrix.to_quaternion()
                
                key.position.x = bone_data.matrix_basis[ 0 ][ 3 ]
                key.position.y = bone_data.matrix_basis[ 1 ][ 3 ]
                key.position.z = bone_data.matrix_basis[ 2 ][ 3 ]
                
                key.orientation.x = -quat.x
                key.orientation.y = -quat.y
                key.orientation.z = -quat.z
                key.orientation.w = quat.w                
                    
                if bone_data.name in bones_keys:
                    bones_keys[ bone_data.name ].append( key )
                else:
                    bones_keys[ bone_data.name ] = [ key ]
        
        for bone_data in action_bones:
            for key in bones_keys[ bone_data.name ]:
                mops.add_anim_key( key )
            
        anim = Animation()
        anim.name = action.name
        anim.bone_count = len( action_bones )
        anim.key_count = frame_count * anim.bone_count
        anim.track_time = int( 1000.0 * frame_count / fps )
        print( "{}({})(b{})".format( action.name, anim.track_time, anim.bone_count ) )
        mops.add_animation( anim )
    
    armature.animation_data.action = restore_action
    scene.frame_set( restore_frame )
    scene.update()
        

def parse_bone( bone, bones_list, vertex_groups, mops ):
    bone_index = len( bones_list )
    
    b = Bone()
    b.name = bone.name
    
    if bone.parent is not None:
        b.parent_name = bone.parent.name
        
    matrix = bone.matrix_local.to_3x3()
    quat = matrix.to_quaternion()
    translation = bone.head_local
    
    b.position.x = translation.x
    b.position.y = translation.y
    b.position.z = translation.z
    
    b.orientation.x = -quat.x
    b.orientation.y = -quat.y
    b.orientation.z = -quat.z
    b.orientation.w = quat.w
    
    if bone.name in vertex_groups:
        b.vertex_count = len( vertex_groups.get( bone.name, [] ) )
        
        for item in vertex_groups[ b.name ]:
            if item[ 1 ] == 0.0:
                b.vertex_count -= 1
                continue
            inf = Influence()
            inf.bone_index = bone_index
            inf.vertex_index = item[ 0 ]
            inf.weight = item[ 1 ]
            mops.add_influence( inf )
            
    bones_list.append( b )
    
    mops.add_bone( b )
    print( "{} done ({} vertices binded).".format( b.name, b.vertex_count) )
    
    for children_bone in bone.children:
        parse_bone( children_bone, bones_list, vertex_groups, mops )
    

def obj_to_mesh( obj ):
    scene = bpy.context.scene
    
    mesh = obj.copy()
    mesh.data = obj.to_mesh( scene, True, 'PREVIEW' )
    
    scene.objects.link( mesh )
    scene.update()
    bpy.ops.object.mode_set( mode = "OBJECT" )
    for item in scene.objects:
        item.select = False

    mesh.select = True
    scene.objects.active = mesh

    bpy.ops.object.mode_set( mode = "EDIT" )
    bpy.ops.mesh.select_all( action = "SELECT" )
    bpy.ops.mesh.quads_convert_to_tris()
    scene.update()
    bpy.ops.object.mode_set( mode = "OBJECT" )

    mesh.data = mesh.to_mesh( scene, False, 'PREVIEW' )
    scene.update()

    return mesh


def find_mesh_and_armature():
    context = bpy.context
    active_object = context.active_object
    armature = None
    
    if active_object and active_object.type == 'MESH':
        if active_object.parent and active_object.parent.type == 'ARMATURE':
            armature = active_object.parent
        return ( active_object, armature )
    else:
        raise Exception( "No mesh selected!" )


def export( file_path ):

    mops = MOPSFile()
    
    active_object, armature = find_mesh_and_armature()
    mesh = obj_to_mesh( active_object )
    
    info = ObjectInfo( active_object.name )
    print( active_object.name )
    mops.add_info( info )
    
    parse_mesh_and_armature( mesh, armature, mops )
    bpy.context.scene.objects.unlink( mesh )
    
    mops.print()
    
    file = open( file_path, "wb" )
    file.write( mops.dump() )
    file.close()
    
    
export( "Script_files/script_test.mops" )