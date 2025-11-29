import json
import os
from PIL import Image, ImageDraw
import numpy as np

# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# File path settings - using absolute paths
division_points_path = os.path.join(script_dir, 'curve_json', 'division_points.json')
# vertex_coordinates_divided.json is in the same curve_json folder
vertex_coordinates_path = os.path.join(script_dir, 'curve_json', 'vertex_coordinates_divided.json')
output_judge_path = os.path.join(script_dir, 'curve_json', 'judge.json')

# Image path settings
image_path = os.path.join(script_dir, 'render_output', 'rendered_image.png')
annotated_image_path = os.path.join(script_dir, 'render_output', 'annotated_image.png')
# New: Path for quadrilaterals image generated directly from vertex_coordinates_divided.json
vertex_divided_quad_image_path = os.path.join(script_dir, 'render_output', 'vertex_divided_quadrilaterals.png')

# Helper function: Check if two points are coincident (within threshold)
def are_points_coincident(point1, point2, tolerance=0.01):
    """Check if two points are coincident within the given tolerance range"""
    return abs(point1[0] - point2[0]) < tolerance and abs(point1[1] - point2[1]) < tolerance

# Helper function: Check if quadrilateral has coincident corners
def has_coincident_corners(corners):
    """Check if the quadrilateral has any adjacent coincident corners"""
    # Check adjacent corners for coincidence (including connection between last and first)
    for i in range(4):
        j = (i + 1) % 4  # Index of the next point, forming a loop
        if are_points_coincident(corners[i], corners[j]):
            return True
    return False

# Create quadrilaterals function - reference logic from divide_vertex_coordinates.py
def create_filtered_quadrilaterals(top_points, bottom_points):
    quadrilaterals = []
    valid_indices = []  # Store original indices of valid quadrilaterals
    # Create as many quadrilaterals as possible, using the minimum length of top and bottom points
    num_quads = min(len(top_points), len(bottom_points)) - 1
    valid_quad_count = 0  # Counter for valid quadrilaterals
    
    for i in range(num_quads):
        # Each quadrilateral consists of four points: top[i], top[i+1], bottom[i+1], bottom[i]
        corners = [
            top_points[i],
            top_points[i+1],
            bottom_points[i+1],
            bottom_points[i]
        ]
        
        # Check if there are coincident corners
        if has_coincident_corners(corners):
            print(f"Warning: Quadrilateral index {i} has coincident corners, skipped")
            print(f"  Corner coordinates: {corners}")
            continue  # Skip this quadrilateral
        
        quad = {
            'id': valid_quad_count,  # Use valid quadrilateral count as ID to ensure continuity
            'corners': corners
        }
        quadrilaterals.append(quad)
        valid_indices.append(i)  # Record the original index of the valid quadrilateral
        valid_quad_count += 1
    
    print(f"Successfully created {len(quadrilaterals)} valid quadrilaterals, skipped {num_quads - len(quadrilaterals)} quadrilaterals with coincident corners")
    return quadrilaterals, valid_indices

# New function: Generate quadrilaterals directly from vertex_coordinates_divided.json and draw them
def generate_quadrilaterals_from_vertex_divided():
    """
    Read all vertex data from vertex_coordinates_divided.json,
    generate quadrilaterals and draw them on an image
    """
    print("\n=== Generating quadrilaterals directly from vertex_coordinates_divided.json ===")
    
    try:
        # Read vertex coordinate data
        print(f"Reading {vertex_coordinates_path}...")
        with open(vertex_coordinates_path, 'r', encoding='utf-8') as f:
            vertex_data = json.load(f)
        
        # Get original top and bottom vertices
        original_top_points = vertex_data.get("original_top_points", [])
        original_bottom_points = vertex_data.get("original_bottom_points", [])
        
        print(f"Read {len(original_top_points)} top points from vertex_coordinates_divided.json")
        print(f"Read {len(original_bottom_points)} bottom points from vertex_coordinates_divided.json")
        
        # Create quadrilaterals
        if original_top_points and original_bottom_points:
            quadrilaterals = create_filtered_quadrilaterals(original_top_points, original_bottom_points)
            print(f"Generated {len(quadrilaterals)} quadrilaterals based on all vertex data")
            
            # Draw quadrilaterals on image
            if os.path.exists(image_path):
                print(f"Reading original image and drawing quadrilaterals...")
                success = draw_quadrilaterals_on_image(image_path, quadrilaterals, vertex_divided_quad_image_path)
                if success:
                    print(f"Quadrilaterals image generated directly from vertex data saved to: {vertex_divided_quad_image_path}")
            else:
                print(f"Warning: Original image {image_path} not found")
                # If no original image, create a blank image to draw quadrilaterals
                if original_top_points and original_bottom_points:
                    # Estimate image size
                    all_points = original_top_points + original_bottom_points
                    x_coords = [p[0] for p in all_points]
                    y_coords = [p[1] for p in all_points]
                    width = int(max(x_coords) * 1.1) if x_coords else 800
                    height = int(max(y_coords) * 1.1) if y_coords else 600
                    
                    # Create blank image
                    print(f"Creating blank image ({width}x{height}) and drawing quadrilaterals...")
                    image = Image.new('RGB', (width, height), color='black')
                    draw = ImageDraw.Draw(image)
                    
                    # Use bright colors
                    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#FF69B4']
                    
                    # Draw each quadrilateral
                    for i, quad in enumerate(quadrilaterals):
                        corners = quad['corners']
                        color = colors[i % len(colors)]
                        draw.polygon(corners, outline=color, width=5)
                        
                        # Add ID label at the center of the quadrilateral
                        center_x = sum(p[0] for p in corners) / 4
                        center_y = sum(p[1] for p in corners) / 4
                        draw.text((center_x - 10, center_y - 10), str(quad['id']), fill='white')
                    
                    # Save image
                    image.save(vertex_divided_quad_image_path)
                    print(f"Quadrilaterals image saved to: {vertex_divided_quad_image_path}")
        else:
            print("Warning: Could not find valid top or bottom vertex data")
            
    except Exception as e:
        print(f"Error generating quadrilaterals from vertex_coordinates_divided.json: {str(e)}")
        import traceback
        traceback.print_exc()

# Read division_points.json and extract all parameter_t values
def extract_parameter_ts():
    with open(division_points_path, 'r', encoding='utf-8') as f:
        division_data = json.load(f)
    
    parameter_ts = []
    for point in division_data['division_points']:
        parameter_ts.append(point['parameter_t'])
    
    return parameter_ts

# Read content from vertex_coordinates_divided.json file
def read_vertex_coordinates():
    with open(vertex_coordinates_path, 'r', encoding='utf-8') as f:
        vertex_data = json.load(f)
    return vertex_data

# Filter vertex data based on parameter_t and summarize
def filter_and_summarize_data(parameter_ts, vertex_data):
    # First create a basic result dictionary without additional fields
    result = {
        "metadata": {
            "total_divisions": len(parameter_ts),
            "source_files": {
                "division_points": division_points_path,
                "vertex_coordinates": vertex_coordinates_path
            }
        },
        "filtered_points": {
            "original_top_points": [],
            "original_bottom_points": [],
            "smoothed_top_points": [],
            "smoothed_bottom_points": []
        }
    }
    
    # Filter vertex data based on parameter_t values
    # parameter_t values range from 0.0 to 1.0, representing proportional positions on the curve
    for point_type in ["original_top_points", "original_bottom_points", "smoothed_top_points", "smoothed_bottom_points"]:
        if point_type in vertex_data:
            points_list = vertex_data[point_type]
            filtered_points = []
            
            # Length of the vertex list
            list_length = len(points_list)
            
            # Find corresponding vertex for each parameter_t value
            for t in parameter_ts:
                # Calculate the corresponding vertex index based on parameter_t value
                # t is a value between 0.0-1.0, representing the relative position in the entire sequence
                # Special handling for t=1.0 to ensure we keep the last point
                if t >= 1.0:
                    mapped_index = list_length - 1
                else:
                    mapped_index = int(t * list_length)
                
                # Ensure the index is within valid range
                if 0 <= mapped_index < list_length:
                    filtered_points.append(points_list[mapped_index])
            
            result["filtered_points"][point_type] = filtered_points
    
    # Regenerate quadrilateral data based on filtered points
    # Use original points to create quadrilaterals (keep consistent with original logic)
    filtered_top_points = result["filtered_points"]["original_top_points"]
    filtered_bottom_points = result["filtered_points"]["original_bottom_points"]
    
    print(f"Number of filtered top points: {len(filtered_top_points)}")
    print(f"Number of filtered bottom points: {len(filtered_bottom_points)}")
    
    filtered_parameter_ts = []
    
    if filtered_top_points and filtered_bottom_points:
        # Create quadrilaterals and get original indices of valid quadrilaterals
        quadrilaterals, valid_indices = create_filtered_quadrilaterals(filtered_top_points, filtered_bottom_points)
        result["quadrilaterals"] = quadrilaterals
        
        # Filter parameter_ts array based on valid quadrilateral indices
        # Note: Each quadrilateral corresponds to two vertices, but we only need to keep the starting position for each quadrilateral
        for idx in valid_indices:
            if idx < len(parameter_ts):
                filtered_parameter_ts.append(parameter_ts[idx])
        
        # Ensure the starting point (first parameter_t value) is preserved
        if parameter_ts and (not filtered_parameter_ts or parameter_ts[0] < filtered_parameter_ts[0]):
            # If the filtered array doesn't contain the starting point, add it to the beginning
            filtered_parameter_ts.insert(0, parameter_ts[0])
        
        # Ensure the ending point (last parameter_t value) is preserved
        if parameter_ts and filtered_parameter_ts and parameter_ts[-1] > filtered_parameter_ts[-1]:
            # If the filtered array doesn't contain the ending point, add it to the end
            filtered_parameter_ts.append(parameter_ts[-1])
        
        print(f"Successfully regenerated {len(result['quadrilaterals'])} quadrilaterals based on filtered points")
        print(f"Number of filtered parameter_ts: {len(filtered_parameter_ts)}")
    else:
        print("Warning: Filtered top or bottom points are empty, unable to generate quadrilaterals")
        result["quadrilaterals"] = []
        filtered_parameter_ts = parameter_ts  # If no quadrilaterals, keep original parameter_ts
    
    # Add filtered parameter_t values
    result["parameter_ts"] = filtered_parameter_ts
    
    # Add curve_tension data
    if "curve_tension" in vertex_data:
        result["curve_tension"] = vertex_data["curve_tension"]
    
    # Add image information
    if "image_path" in vertex_data:
        result["image_path"] = vertex_data["image_path"]
    if "image_size" in vertex_data:
        result["image_size"] = vertex_data["image_size"]
    
    return result

# Draw quadrilaterals on image
def draw_quadrilaterals_on_image(image_path, quadrilaterals, output_path):
    try:
        # Open original image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Use bright colors for better visibility on black background
        colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#FF69B4']
        
        # Draw each quadrilateral
        for i, quad in enumerate(quadrilaterals):
            # Get the four corners of the quadrilateral
            corners = quad['corners']
            # Select color
            color = colors[i % len(colors)]
            # Draw quadrilateral outline - increase line width to 5px for thicker dividing lines
            draw.polygon(corners, outline=color, width=5)
            
            # Add ID label at the center of the quadrilateral
            # Calculate center coordinates
            center_x = sum(p[0] for p in corners) / 4
            center_y = sum(p[1] for p in corners) / 4
            # Add text label - use white text for better visibility on black background
            draw.text((center_x - 10, center_y - 10), str(quad['id']), fill='white')
        
        # Save annotated image
        image.save(output_path)
        print(f"Annotated image saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error drawing quadrilaterals: {str(e)}")
        return False

# Save result to judge.json file
def save_judge_json(result):
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_judge_path), exist_ok=True)
    
    with open(output_judge_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"judge.json saved to: {output_judge_path}")

# Main function
def main():
    print("Starting data processing...")
    
    # Step 1: Extract parameter_t values
    print(f"Reading {division_points_path} and extracting parameter_t values...")
    parameter_ts = extract_parameter_ts()
    print(f"Extracted {len(parameter_ts)} parameter_t values in total")
    
    # Step 2: Read vertex coordinate data
    print(f"Reading {vertex_coordinates_path}...")
    vertex_data = read_vertex_coordinates()
    
    # Print basic information about vertex data
    top_points_len = len(vertex_data.get("original_top_points", []))
    bottom_points_len = len(vertex_data.get("original_bottom_points", []))
    print(f"Number of top points in vertex_coordinates_divided.json: {top_points_len}")
    print(f"Number of bottom points in vertex_coordinates_divided.json: {bottom_points_len}")
    
    # Step 3: Filter and summarize data
    print("Filtering and summarizing data...")
    result = filter_and_summarize_data(parameter_ts, vertex_data)
    
    # Step 4: Save result
    save_judge_json(result)
    
    # Step 5: Draw quadrilaterals on image
    if 'quadrilaterals' in result and result['quadrilaterals']:
        print(f"Found {len(result['quadrilaterals'])} quadrilaterals, preparing to draw on image...")
        if os.path.exists(image_path):
            print(f"Reading original image: {image_path}")
            draw_quadrilaterals_on_image(image_path, result['quadrilaterals'], annotated_image_path)
        else:
            print(f"Warning: Original image {image_path} not found")
    else:
        print("No quadrilateral data found, skipping drawing step")
    
    # Step 6: New feature - Generate quadrilaterals image directly from vertex_coordinates_divided.json
    generate_quadrilaterals_from_vertex_divided()
    
    print("Data processing completed!")

if __name__ == "__main__":
    main()