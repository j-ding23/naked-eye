# -*- coding: utf-8 -*-
"""
Vertex Coordinate Processing Module

This module contains functions for reading vertex coordinates, dividing points,
creating quadrilaterals, and generating JSON data.
"""

import os
import json
from PIL import Image, ImageDraw

def read_vertex_coordinates(file_path):
    """Read vertex coordinate file"""
    points = []
    with open(file_path, 'r', encoding='utf-8') as f:
        # Skip header line
        next(f)
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 7:
                vertex_id = int(parts[0].strip())
                world_x = float(parts[1].strip())
                world_y = float(parts[2].strip())
                world_z = float(parts[3].strip())
                screen_x = float(parts[4].strip())
                screen_y = float(parts[5].strip())
                depth = float(parts[6].strip())
                
                points.append({
                    'vertex_id': vertex_id,
                    'world_coordinates': (world_x, world_y, world_z),
                    'screen_coordinates': (screen_x, screen_y),
                    'depth': depth
                })
    return points

def divide_points_by_mid_y(points):
    """Divide points into top and bottom parts"""
    # Calculate the midpoint of all SCREEN_Y values
    screen_ys = [point['screen_coordinates'][1] for point in points]
    min_y = min(screen_ys)
    max_y = max(screen_ys)
    mid_y = (min_y + max_y) / 2
    
    # Split points
    top_points = []
    bottom_points = []
    
    for point in points:
        screen_x, screen_y = point['screen_coordinates']
        if screen_y < mid_y:
            top_points.append([screen_x, screen_y])
        else:
            bottom_points.append([screen_x, screen_y])
    
    # Sort by x-coordinate to arrange points in order
    top_points.sort(key=lambda p: p[0])
    bottom_points.sort(key=lambda p: p[0])
    
    return top_points, bottom_points, mid_y

def create_quadrilaterals(top_points, bottom_points):
    """Create quadrilaterals"""
    quadrilaterals = []
    # Create as many quadrilaterals as possible using the minimum length of top and bottom points
    num_quads = min(len(top_points), len(bottom_points)) - 1
    
    for i in range(num_quads):
        # Each quadrilateral consists of four points: top[i], top[i+1], bottom[i+1], bottom[i]
        quad = {
            'id': i,
            'corners': [
                top_points[i],
                top_points[i+1],
                bottom_points[i+1],
                bottom_points[i]
            ]
        }
        quadrilaterals.append(quad)
    
    return quadrilaterals

def generate_json_data(top_points, bottom_points, quadrilaterals):
    """Generate JSON data"""
    # Assumed image size
    image_size = {
        'width': 1920,
        'height': 1080
    }
    
    # Create JSON data structure
    json_data = {
        'image_path': 'rendered_image.png',
        'image_size': image_size,
        'original_top_points': top_points,
        'original_bottom_points': bottom_points,
        'smoothed_top_points': top_points,
        'smoothed_bottom_points': bottom_points,
        'quadrilaterals': quadrilaterals,
        'curve_tension': 0.5
    }
    
    return json_data

def draw_quadrilaterals_on_image(image_path, quadrilaterals, output_path):
    """Draw quadrilaterals on image"""
    try:
        # Open original image
        image = Image.open(image_path)
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
        
        # Save annotated image
        image.save(output_path)
        print(f"Quadrilateral annotated image saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error drawing quadrilaterals: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main(vertex_file_path, rendered_image_path, output_json_path, output_image_path):
    """Main function: Process vertex coordinates and generate quadrilateral data"""
    print(f"Reading vertex coordinate file: {vertex_file_path}")
    points = read_vertex_coordinates(vertex_file_path)
    print(f"Successfully read {len(points)} vertex coordinates")
    
    print("Dividing points into top and bottom parts...")
    top_points, bottom_points, mid_y = divide_points_by_mid_y(points)
    print(f"Mid Y value: {mid_y}")
    print(f"Number of top points: {len(top_points)}")
    print(f"Number of bottom points: {len(bottom_points)}")
    
    print("Creating quadrilaterals...")
    quadrilaterals = create_quadrilaterals(top_points, bottom_points)
    print(f"Created {len(quadrilaterals)} quadrilaterals")
    
    print("Generating JSON data...")
    json_data = generate_json_data(top_points, bottom_points, quadrilaterals)
    
    print(f"Saving results to: {output_json_path}")
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print("Drawing quadrilaterals on image...")
    draw_quadrilaterals_on_image(rendered_image_path, quadrilaterals, output_image_path)
    
    return json_data

if __name__ == "__main__":
    # If running this script directly, use default paths
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set default paths
    default_paths = {
        'vertex_file': os.path.join(script_dir, 'render_output', 'vertex_coordinates.txt'),
        'rendered_image': os.path.join(script_dir, 'render_output', 'rendered_image.png'),
        'output_json': os.path.join(script_dir, 'curve_json', 'vertex_coordinates_divided.json'),
        'output_image': os.path.join(script_dir, 'render_output', 'quadrilaterals_annotated.png')
    }
    
    # Execute main function
    main(
        default_paths['vertex_file'],
        default_paths['rendered_image'],
        default_paths['output_json'],
        default_paths['output_image']
    )
