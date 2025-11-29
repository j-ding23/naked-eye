# -*- coding: utf-8 -*-
"""
Integrated Workflow: Image Annotation and Perspective Transformation

This script integrates the following functionalities and executes them in order:
1. Annotate vertex coordinates on rendered image
2. Read quadrilateral data from judge.json and perform perspective transformation to generate strip images
"""

import os
import json
import sys
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Set file paths
def get_file_paths():
    """Get all required file paths - using relative paths"""
    # Using relative paths, relative to the script's current working directory (github directory)
    return {
        'rendered_image': "./render_output/rendered_image.png",
        'vertex_file': "./render_output/vertex_coordinates.txt",
        'annotated_image': "./render_output/annotated_image.png",
        'judge_json': "./curve_json/judge.json",  # 使用judge.json代替output_json
        'division_points_json': "./curve_json/division_points.json",
        'output_dir': "./strip_transformed"
    }

# 从judge.json读取四边形数据
def load_quadrilaterals_from_json(json_path):
    """Read quadrilateral data and related information from judge.json file"""
    try:
        print(f"Reading quadrilateral data from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Read vertex data (support two formats based on actual structure)
        if 'filtered_points' in data:
            # Format 1: Vertex data in filtered_points
            filtered_points = data.get('filtered_points', {})
            top_points = filtered_points.get('original_top_points', [])
            bottom_points = filtered_points.get('original_bottom_points', [])
        else:
            # Format 2: Vertex data directly at the top level
            top_points = data.get('original_top_points', [])
            bottom_points = data.get('original_bottom_points', [])
        
        # 获取四边形数据
        quadrilaterals = data.get('quadrilaterals', [])
        
        print(f"Successfully read {len(quadrilaterals)} quadrilaterals")
        print(f"Read {len(top_points)} top points, {len(bottom_points)} bottom points")
        
        return quadrilaterals, top_points, bottom_points
    except Exception as e:
        print(f"Error reading quadrilateral data: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], [], []

# Draw quadrilaterals (keep this function for image annotation)
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

# ===== Part 2: Image Vertex Annotation =====
def annotate_image(rendered_image_path, vertex_file_path, output_image_path):
    """Annotate vertex coordinates on rendered image"""
    try:
        # Read image
        image = Image.open(rendered_image_path)
        draw = ImageDraw.Draw(image)
        
        # Try loading Chinese font, use default font if unavailable
        try:
            # Try using system Chinese font
            if sys.platform.startswith('win'):
                font = ImageFont.truetype("simhei.ttf", 12)  # Windows system
            else:
                font = ImageFont.truetype("Arial Unicode MS", 12)  # Other systems
        except:
            # Use default font
            font = ImageFont.load_default()
        
        # Read and annotate vertex coordinates
        with open(vertex_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[1:]  # Skip header line
            
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) >= 6:
                    vertex_id = int(parts[0])
                    screen_x = float(parts[4])
                    screen_y = float(parts[5])
                    
                    # Annotate point on image
                    draw.ellipse([(screen_x-3, screen_y-3), (screen_x+3, screen_y+3)], fill=(255, 0, 0), outline=(0, 0, 0))
                    
                    # Annotate vertex ID on image
                    draw.text((screen_x+5, screen_y-10), f"{vertex_id}", fill=(0, 0, 0), font=font)
        
        # Save annotated image
        image.save(output_image_path)
        print(f"Vertex annotated image saved to: {output_image_path}")
        return True
    except Exception as e:
        print(f"Error annotating image: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# ===== Part 3: Perspective Transformation =====
def sort_corners(corners):
    """Sort the four corners of a quadrilateral"""
    corners = np.array(corners)
    center = np.mean(corners, axis=0)
    top_points = []
    bottom_points = []
    for corner in corners:
        if corner[1] < center[1]:
            top_points.append(corner)
        else:
            bottom_points.append(corner)
    top_points = sorted(top_points, key=lambda p: p[0])
    bottom_points = sorted(bottom_points, key=lambda p: p[0])
    if len(top_points) == 1 and len(bottom_points) == 3:
        min_y = min(bottom_points, key=lambda p: p[1])
        bottom_points.remove(min_y)
        top_points.append(min_y)
        top_points = sorted(top_points, key=lambda p: p[0])
    elif len(top_points) == 3 and len(bottom_points) == 1:
        max_y = max(top_points, key=lambda p: p[1])
        top_points.remove(max_y)
        bottom_points.append(max_y)
        bottom_points = sorted(bottom_points, key=lambda p: p[0])
    return [top_points[0], top_points[1], bottom_points[1], bottom_points[0]]

def sample_with_perspective_transform(target_img, quad_corners, out_w, out_h):
    """Sample from quadrilateral using OpenCV perspective transform"""
    img = target_img
    
    # Use OpenCV for perspective transformation
    src_pts = np.array(quad_corners, dtype=np.float32)
    
    # Define the four vertices of the target rectangle
    dst_pts = np.array([[0, 0], [out_w-1, 0], [out_w-1, out_h-1], [0, out_h-1]], dtype=np.float32)
    
    # Calculate perspective transformation matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    
    # Apply perspective transformation
    out = cv2.warpPerspective(img, M, (out_w, out_h), flags=cv2.INTER_LINEAR)
    
    return out

def transform_with_strip_interpolation(annotation_file, target_image_path, output_dir, strip_width=10, edge_strip_width=10, width_proportions_json=None, total_width=None):
    """Perform perspective transformation on quadrilateral areas and generate strip images"""
    # Record start time
    start_time = time.time()
    
    # Clear output directory to avoid interference from previous files
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(output_dir)

    try:
        # Use relative paths directly to ensure correct reading of files with Chinese characters
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Use PIL to read image, then convert to OpenCV format for better handling of Chinese paths
        try:
            pil_img = Image.open(target_image_path)
            # Convert PIL image to OpenCV format (RGB -> BGR)
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            print(f"Successfully read image: {target_image_path}, size: {img.shape}")
        except Exception as e:
            print(f"Failed to read image with PIL: {e}")
            # As an alternative, try using cv2.imread
            img = cv2.imread(target_image_path)
            if img is None:
                print(f"Cannot read target image: {target_image_path}")
                return False
            print(f"Successfully read image with cv2: {target_image_path}, size: {img.shape}")

        H = img.shape[0]
        out_h = int(H)

        # Generate strip widths
        num_quads = len(data["quadrilaterals"])
        widths = []
        
        # Get parameter_ts array directly from judge.json (already included in the passed data)
        try:
            # Get parameter_ts array directly from judge.json data
            parameter_ts = data.get("parameter_ts", [])
            
            # Calculate the difference of parameter_t values as width ratios
            if len(parameter_ts) >= 2 and (len(parameter_ts) - 1) == num_quads:
                # Calculate the difference between adjacent parameter_t values
                diff_values = []
                for i in range(num_quads):
                    diff = parameter_ts[i+1] - parameter_ts[i]
                    diff_values.append(diff)
                
                # Calculate each strip width
                for i in range(num_quads):
                    width = int(diff_values[i] * total_width)
                    # Ensure width is at least 1 pixel
                    widths.append(max(1, width))
                print(f"Successfully obtained {len(parameter_ts)} parameter_ts values from judge.json, generated {num_quads} difference width values")
            else:
                print(f"Warning: The number of parameter_ts values({len(parameter_ts)}) does not match the differential requirement with the number of quadrilaterals({num_quads}), using default width")
                print(f"Required: parameter_ts count = number of quadrilaterals + 1")
                # Fall back to default width calculation
                for i in range(num_quads):
                    widths.append(int(edge_strip_width) if (i == 0 or i == num_quads - 1) else int(strip_width))
        except Exception as e:
            print(f"Warning: Failed to read parameter_ts from judge.json: {e}, using default width")
            # Fall back to default width calculation
            for i in range(num_quads):
                widths.append(int(edge_strip_width) if (i == 0 or i == num_quads - 1) else int(strip_width))

        # Ensure widths array length matches number of quadrilaterals
        if len(widths) != num_quads:
            print(f"Warning: Width array length({len(widths)}) does not match number of quadrilaterals({num_quads}), recalculating default widths")
            widths = []
            for i in range(num_quads):
                widths.append(int(edge_strip_width) if (i == 0 or i == num_quads - 1) else int(strip_width))

        print(f"Processing {num_quads} quadrilaterals in total, width array length: {len(widths)}")

        # Process each quadrilateral
        for index, quad in enumerate(data["quadrilaterals"]):
            qid = quad["id"]
            corners = sort_corners(quad["corners"])  # Top-left, top-right, bottom-right, bottom-left
            
            # Ensure index is within valid range
            if index < len(widths):
                out_w = widths[index]
                
                # Special handling for the last quadrilateral to avoid excessive width
                if index == num_quads - 1 and out_w > 100:  # If the last strip width exceeds 100 pixels
                    print(f"Note: Last quadrilateral(ID={qid}) width({out_w}) is too large, adjusting to 50 pixels")
                    out_w = 50
                
                print(f"Processing quadrilateral ID={qid}, width={out_w}px, corner count={len(corners)}")
                
                try:
                    warped = sample_with_perspective_transform(img, corners, out_w, out_h)
                    out_name = os.path.join(output_dir, f"strip_quadrilateral_{qid:02d}_transformed.png")
                    cv2.imwrite(out_name, warped)
                except Exception as e:
                    print(f"Error processing quadrilateral ID={qid}: {e}")

        # Create preview with separator lines and IDs
        if widths:
            gap = 5
            vis_w = sum(widths) + (num_quads - 1) * gap
            vis = np.zeros((out_h, vis_w, 3), dtype=np.uint8)
            x = 0
            for index, quad in enumerate(data["quadrilaterals"]):
                qid = quad["id"]
                path = os.path.join(output_dir, f"strip_quadrilateral_{qid:02d}_transformed.png")
                if os.path.exists(path):
                    tile = cv2.imread(path)
                    if tile is not None:
                        w = tile.shape[1]
                        vis[:, x:x+w] = tile
                        if x > 0:
                            cv2.line(vis, (x-2, 0), (x-2, out_h), (255,255,255), 1)
                        cv2.putText(vis, f"Q{qid}", (x+2, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                        x += w + gap

            cv2.imwrite(os.path.join(output_dir, "strip_all_transformed_quadrilaterals.png"), vis)

            # Generate seamless concatenated image without separator lines or IDs
            seamless_w = sum(widths)
            seamless = np.zeros((out_h, seamless_w, 3), dtype=np.uint8)
            x = 0
            for index, quad in enumerate(data["quadrilaterals"]):
                qid = quad["id"]
                path = os.path.join(output_dir, f"strip_quadrilateral_{qid:02d}_transformed.png")
                if os.path.exists(path):
                    tile = cv2.imread(path)
                    if tile is not None:
                        w = tile.shape[1]
                        seamless[:, x:x+w] = tile
                        x += w

            cv2.imwrite(os.path.join(output_dir, "strip_all_transformed_quadrilaterals_seamless.png"), seamless)
        
        # Record end time and calculate elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total time taken for perspective transformation: {elapsed_time:.2f} seconds")
        return True
    except Exception as e:
        print(f"Error during perspective transformation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# ===== Main Workflow =====
def main():
    """Main workflow: Execute two steps in sequence"""
    print("=== Starting integrated workflow ===")
    
    # Get file paths
    paths = get_file_paths()
    
    # Check if necessary files exist
    if not os.path.exists(paths['rendered_image']):
        print(f"Error: Rendered image not found: {paths['rendered_image']}")
        print("Please run blender_vertex_script.py in Blender first to generate the rendered image")
        return
    
    if not os.path.exists(paths['vertex_file']):
        print(f"Error: Vertex coordinate file not found: {paths['vertex_file']}")
        print("Please run blender_vertex_script.py in Blender first to generate the vertex coordinate file")
        return
    
    if not os.path.exists(paths['judge_json']):
        print(f"Error: Quadrilateral data file not found: {paths['judge_json']}")
        print("Please run vertex_processor.py first to generate quadrilateral data")
        return
    
    # Step 1: Read quadrilateral data from judge.json
    print("\n=== Step 1: Read quadrilateral data from judge.json ===")
    quadrilaterals, top_points, bottom_points = load_quadrilaterals_from_json(paths['judge_json'])
    
    if not quadrilaterals:
        print("Error: Failed to read quadrilateral data, program exiting")
        return
    
    print("Drawing quadrilaterals on image...")
    quad_annotated_path = os.path.join(os.path.dirname(paths['annotated_image']), "quadrilaterals_annotated.png")
    draw_quadrilaterals_on_image(paths['rendered_image'], quadrilaterals, quad_annotated_path)
    
    # Step 2: Image vertex annotation
    print("\n=== Step 2: Image vertex annotation ===")
    print("Starting image annotation...")
    annotate_image(paths['rendered_image'], paths['vertex_file'], paths['annotated_image'])
    print("Vertex annotation completed!")
    
    # Step 3: Perspective transformation
    print("\n=== Step 3: Perspective transformation ===")
    print("Starting perspective transformation processing...")
    
    # Check if division_points.json exists
    if not os.path.exists(paths['division_points_json']):
        print(f"Warning: division_points.json file not found: {paths['division_points_json']}")
        print("Will use default width for perspective transformation")
        division_points_path = None
    else:
        division_points_path = paths['division_points_json']
        print(f"Will use division_points.json file: {division_points_path}")
    
    # Use judge.json as input file for perspective transformation, pass division_points.json path as width_proportions_json
    success = transform_with_strip_interpolation(
        paths['judge_json'], 
        paths['rendered_image'], 
        paths['output_dir'],
        width_proportions_json=division_points_path,
        total_width=1920
    )
    
    if success:
        print("Perspective transformation completed!")
        print(f"Generated strip images are saved in: {paths['output_dir']}")
    
    print("\n=== Integrated workflow completed ===")
    print(f"Quadrilateral data file path: {paths['judge_json']}")
    print(f"Quadrilateral annotated image path: {quad_annotated_path}")
    print(f"Vertex annotated image path: {paths['annotated_image']}")
    print(f"Strip transformation results directory: {paths['output_dir']}")

if __name__ == "__main__":
    main()
