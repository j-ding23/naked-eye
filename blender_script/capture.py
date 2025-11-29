import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import os
import sys
import math

# Set UTF-8 encoding
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def get_vertex_screen_coordinates(object_name, camera_name, scene):
    """
    Calculate object vertices' coordinates on camera render
    Including modifier effects (such as curve modifiers)
    """
    # Get object and camera
    obj = bpy.data.objects.get(object_name)
    camera = bpy.data.objects.get(camera_name)
    
    if not obj:
        raise ValueError(f"Object '{object_name}' does not exist")
    if not camera:
        raise ValueError(f"Camera '{camera_name}' does not exist")
    if obj.type != 'MESH':
        raise ValueError(f"Object '{object_name}' is not a mesh type")
    if camera.type != 'CAMERA':
        raise ValueError(f"Object '{camera_name}' is not a camera type")
    
    # Key modification: Use to_mesh() to get mesh data with modifiers applied
    # This will include the effects of all modifiers like curve modifiers
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    
    # Get world matrix (for the modified object)
    obj_matrix = obj.matrix_world
    
    coordinates = []
    
    # Iterate through all vertices
    for vertex in mesh.vertices:
        # Get world coordinates of the vertex
        world_coords = obj_matrix @ vertex.co
        
        # Convert to camera view coordinates (normalized coordinates)
        camera_coords = world_to_camera_view(scene, camera, world_coords)
        
        # Convert to screen pixel coordinates
        screen_x = camera_coords.x * scene.render.resolution_x
        screen_y = scene.render.resolution_y - (camera_coords.y * scene.render.resolution_y)
        depth = camera_coords.z
        
        coordinates.append({
            'vertex_index': vertex.index,
            'world_coordinates': (world_coords.x, world_coords.y, world_coords.z),
            'screen_coordinates': (round(screen_x, 2), round(screen_y, 2)),
            'depth': round(depth, 4)
        })
    
    # Clean up temporary mesh data
    eval_obj.to_mesh_clear()
    
    return coordinates

def calculate_vertex_distances(coordinates):
    """
    Calculate distances between adjacent vertices and normalize them (sum to 1)
    """
    distances = []
    total_distance = 0.0
    
    # Sort by vertex index
    sorted_coords = sorted(coordinates, key=lambda x: x['vertex_index'])
    
    # Calculate distances between adjacent vertices
    for i in range(len(sorted_coords) - 1):
        # Get world coordinates of current vertex and next vertex
        v1 = Vector(sorted_coords[i]['world_coordinates'])
        v2 = Vector(sorted_coords[i+1]['world_coordinates'])
        
        # Calculate Euclidean distance
        distance = (v2 - v1).length
        distances.append(distance)
        total_distance += distance
    
    # Normalize distances (sum to 1)
    normalized_distances = []
    if total_distance > 0:
        normalized_distances = [d / total_distance for d in distances]
    
    return distances, normalized_distances

def list_scene_objects():
    """
    List all objects and camera names in the scene
    """
    print("Mesh objects in scene:")
    print("--------------------")
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if not mesh_objects:
        print("No mesh objects found")
    else:
        for obj in mesh_objects:
            print(f"- {obj.name}")
    
    print("\nCameras in scene:")
    print("--------------------")
    cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
    if not cameras:
        print("No cameras found")
    else:
        for camera in cameras:
            print(f"- {camera.name}")

def main():
    try:
        print("="*50)
        print("Blender Vertex Screen Coordinates Calculator")
        print("Blender Vertex Screen Coordinates Calculator")
        print("="*50)
        
        # Get current scene
        scene = bpy.context.scene
        
        # List all objects and cameras in the scene
        list_scene_objects()
        
        # Configuration parameters - modify these values according to your scene
        object_name = "wan.002"  # Name of the object to analyze
        camera_name = "Camera.004"  # Name of the camera to use
        
        # Get file save path
        blend_file_path = bpy.path.abspath("//")
        output_dir = os.path.join(blend_file_path, "../render_output")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Set output file paths
        rendered_image = os.path.join(output_dir, "rendered_image.png")
        vertex_file = os.path.join(output_dir, "vertex_coordinates.txt")
        
        print(f"\nUsing object: {object_name}")
        print(f"Using camera: {camera_name}")
        print(f"Output directory: {output_dir}")
        
        # Set render camera
        camera = bpy.data.objects.get(camera_name)
        if not camera:
            raise ValueError(f"Camera '{camera_name}' does not exist")
        scene.camera = camera
        
        # Set render output path
        scene.render.filepath = rendered_image
        
        # Execute rendering
        print(f"\nStarting to render view from camera '{camera_name}'...")
        bpy.ops.render.render(write_still=True)
        print(f"Rendering completed, image saved to: {scene.render.filepath}")
        
        # Calculate vertex screen coordinates
        print(f"\nCalculating vertex coordinates for object '{object_name}'...")
        coordinates = get_vertex_screen_coordinates(object_name, camera_name, scene)
        
        # Save vertex coordinates to file
        with open(vertex_file, "w", encoding="utf-8") as f:
            # Write vertex coordinates
            f.write("VERTEX_ID, WORLD_X, WORLD_Y, WORLD_Z, SCREEN_X, SCREEN_Y, DEPTH\n")
            for coord in coordinates:
                f.write(f"{coord['vertex_index']}, {coord['world_coordinates'][0]:.2f}, {coord['world_coordinates'][1]:.2f}, {coord['world_coordinates'][2]:.2f}, {coord['screen_coordinates'][0]:.2f}, {coord['screen_coordinates'][1]:.2f}, {coord['depth']:.4f}\n")
            
            # Write separator line
            f.write("\n----Normalized Distances Between Vertices----\n")
            f.write("SEGMENT_INDEX, NORMALIZED_DISTANCE\n")
            
            # Calculate and normalize distances between adjacent vertices
            distances, normalized_distances = calculate_vertex_distances(coordinates)
            
            # Write normalized distances
            for i, norm_dist in enumerate(normalized_distances):
                f.write(f"{i}, {norm_dist:.6f}\n")
        
        print(f"Vertex coordinates saved to: {vertex_file}")
        print(f"Calculated and saved {len(normalized_distances)} segments of normalized distances between adjacent vertices")
        print("\nOperation completed!")
        print(f"\nOutput files saved to:")
        print(f"1. Rendered image: {rendered_image}")
        print(f"2. Vertex coordinates file: {vertex_file}")
        print(f"\nTips:\n1. You can use annotate_vertex_image.py script to annotate images externally\n2. After rendering, you can run run_annotation_tool.py to start the flexible quadrilateral annotation tool")
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()