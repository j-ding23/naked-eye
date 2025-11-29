import bpy
import math
import os
import json
from mathutils import Vector

# Try to import PIL library for drawing
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    print("Warning: PIL library is not available, some drawing functions may be limited")
    PIL_AVAILABLE = False

# 保存细分点数据用于后续绘制
saved_subdivision_points = []

def process_bezier_spline(spline, curve_object, viewpoint, sample_count):
    """
    Process Bezier curve (simplified version)
    """
    world_matrix = curve_object.matrix_world
    points_data = []
    
    # 遍历每个贝塞尔段
    point_count = len(spline.bezier_points)
    segments = range(point_count if spline.use_cyclic_u else point_count - 1)
    
    for i in segments:
        # 获取当前点和下一个点
        p1 = spline.bezier_points[i]
        p2 = spline.bezier_points[(i + 1) % point_count] if spline.use_cyclic_u else spline.bezier_points[i + 1]
        
        # 计算分段采样数量
        seg_samples = sample_count // (point_count if spline.use_cyclic_u else point_count - 1)
        
        # 计算段点数据
        segment_points = calculate_bezier_segment_points(p1, p2, world_matrix, viewpoint, seg_samples)
        points_data.extend(segment_points)
    
    # 计算细分点并返回
    return calculate_and_visualize_subdivision(points_data, curve_object)

def calculate_bezier_segment_points(p1, p2, world_matrix, viewpoint, segment_samples):
    """
    Simplified version: Calculate Bezier curve segment points data
    """
    points = []
    
    # 获取控制点并应用世界变换
    p0 = world_matrix @ p1.co
    h0 = world_matrix @ p1.handle_right
    h1 = world_matrix @ p2.handle_left
    p1_world = world_matrix @ p2.co
    
    # 对每个段进行采样
    for i in range(segment_samples + 1):
        t = i / segment_samples
        
        # 计算贝塞尔曲线上的点
        point = bezier_point(p0, h0, h1, p1_world, t)
        
        # 简化：只存储点信息，不再计算复杂的曲率和密度
        points.append({
            'point': point,
            't': t
        })
    
    return points

def bezier_point(p0, p1, p2, p3, t):
    """
    Simplified version: Calculate point on Bezier curve
    """
    t_inv = 1 - t
    return (
        t_inv**3 * p0 +
        3 * t_inv**2 * t * p1 +
        3 * t_inv * t**2 * p2 +
        t**3 * p3
    )

# Simplified version only retains Bezier point calculation function, removing unused derivative and curvature calculations

# Removed unused vector angle calculation function

def process_nurbs_spline(spline, curve_object, viewpoint, sample_count):
    """
    Process NURBS curve (simplified version)
    """
    world_matrix = curve_object.matrix_world
    points_data = []
    
    # 简化的NURBS曲线采样 - 仅收集点数据
    for i in range(sample_count + 1):
        t = i / sample_count
        point = evaluate_nurbs_curve(spline, t, world_matrix)
        
        # 简化：只存储点信息，不再计算复杂的曲率和密度参数
        points_data.append({
            'point': point,
            't': t
        })
    
    # 计算细分点
    return calculate_and_visualize_subdivision(points_data, curve_object)

def evaluate_nurbs_curve(spline, t, world_matrix):
    """
    Simplified version: Evaluate point on NURBS curve
    Use linear interpolation for simplified calculation
    """
    points = spline.points
    num_points = len(points)
    
    if num_points == 0:
        return Vector((0, 0, 0))
    elif num_points == 1:
        return world_matrix @ Vector(points[0].co[:3]) / points[0].co.w
    
    # 简单的线性插值
    index = min(int(t * (num_points - 1)), num_points - 2)
    t_local = t * (num_points - 1) - index
    
    # 获取两个控制点
    p1 = Vector(points[index].co[:3]) / points[index].co.w
    p2 = Vector(points[index + 1].co[:3]) / points[index + 1].co.w
    
    # 线性插值
    point = p1 + (p2 - p1) * t_local
    
    # 应用世界变换
    return world_matrix @ point

def calculate_and_visualize_subdivision(points_data, curve_object=None):
    """
    Simplified version: Calculate subdivision points
    """
    # Directly use points from data as subdivision points (simplified processing)
    subdivision_points = [data['point'] for data in points_data]
    visualize_subdivision_points(subdivision_points)
    return subdivision_points

def visualize_subdivision_points(points):
    """
    Save subdivision point data for subsequent drawing, no longer creating visualization objects in Blender
    """
    # Only save point data for drawing
    global saved_subdivision_points
    saved_subdivision_points = points.copy()
    print(f"Saved {len(points)} subdivision points data for drawing")
    
    return points

# Removed unused curvature subdivision function

# Removed unused camera setup function

# Only draw curve structure and save as image
def draw_curve_structure_only(curve_object, output_file=None, camera_coords=None, use_camera_as_origin=False):
    """
    Draw the smooth structure of the curve and optionally mark camera position
    
    Parameters:
        curve_object: The curve object to draw
        output_file: Optional, output file name
        camera_coords: Optional, camera world coordinates (Vector), if provided, will mark camera position on the image
        use_camera_as_origin: Optional, whether to use camera coordinates as origin (0,0,0) for drawing
    """
    # Use user-specified folder path - use raw string format to avoid Unicode escape errors
    output_dir = r"c:\Users\华为\Desktop\bltopo\blender_curve_subdivision"
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if output_file:
        output_path = os.path.join(output_dir, output_file)
    else:
        output_path = os.path.join(output_dir, f"curve_structure_{curve_object.name}.png")
    
    # 用于存储曲线上所有采样点的列表
    curve_points = []
    world_matrix = curve_object.matrix_world
    
    for spline in curve_object.data.splines:
        if spline.type == 'BEZIER':
            # 贝塞尔曲线：使用密集采样确保曲线平滑
            for i, point in enumerate(spline.bezier_points):
                # 检查是否需要连接到下一个点
                if i < len(spline.bezier_points) - 1 or spline.use_cyclic_u:
                    next_point = spline.bezier_points[(i + 1) % len(spline.bezier_points)]
                    
                    # 密集采样贝塞尔曲线以获得平滑效果
                    # 增加采样密度以确保曲线平滑度
                    for t in range(0, 101):
                        t_val = t / 100  # 使用0到1之间的100个采样点
                        
                        # 获取四个控制点（包括手柄）
                        p0 = world_matrix @ point.co
                        p1 = world_matrix @ point.handle_right
                        p2 = world_matrix @ next_point.handle_left
                        p3 = world_matrix @ next_point.co
                        
                        # 计算贝塞尔曲线上的点
                        x = (1-t_val)**3 * p0.x + 3*(1-t_val)**2*t_val*p1.x + 3*(1-t_val)*t_val**2*p2.x + t_val**3*p3.x
                        y = (1-t_val)**3 * p0.y + 3*(1-t_val)**2*t_val*p1.y + 3*(1-t_val)*t_val**2*p2.y + t_val**3*p3.y
                        
                        # 如果使用摄像机作为原点，则将坐标转换为摄像机坐标系
                        if use_camera_as_origin and camera_coords:
                            x = x - camera_coords.x
                            y = y - camera_coords.y
                        
                        curve_points.append((x, y))
        elif spline.type == 'NURBS':
            # NURBS曲线：使用密集采样以显示平滑曲线
            num_samples = 200  # 增加采样点数以获得更平滑的曲线
            for t in range(num_samples + 1):
                t_val = t / num_samples
                point = evaluate_nurbs_curve(spline, t_val, world_matrix)
                
                # 如果使用摄像机作为原点，则将坐标转换为摄像机坐标系
                x = point.x
                y = point.y
                if use_camera_as_origin and camera_coords:
                    x = x - camera_coords.x
                    y = y - camera_coords.y
                
                curve_points.append((x, y))
    
    # 简化的坐标转换和绘图
    try:
        from PIL import Image, ImageDraw
        
        # 创建图像和基本设置
        img_width, img_height = 800, 600
        image = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 简化的坐标映射
        if curve_points:
            min_x, min_y = min(p[0] for p in curve_points), min(p[1] for p in curve_points)
            max_x, max_y = max(p[0] for p in curve_points), max(p[1] for p in curve_points)
            
            # 避免除零错误
            width_range = max_x - min_x if max_x != min_x else 1
            height_range = max_y - min_y if max_y != min_y else 1
            
            margin = 50
            scale = min((img_width-2*margin)/width_range, 
                        (img_height-2*margin)/height_range)
            
            # 坐标转换
            def map_point(pt):
                x = margin + (pt[0]-min_x) * scale
                y = img_height - margin - (pt[1]-min_y) * scale
                return (x, y)
            
            # 绘制XY坐标轴
            # X轴
            x_axis_start = map_point((min_x, 0))
            x_axis_end = map_point((max_x, 0))
            draw.line([x_axis_start, x_axis_end], fill=(255, 0, 0, 255), width=2)  # 红色X轴
            
            # Y轴
            y_axis_start = map_point((0, min_y))
            y_axis_end = map_point((0, max_y))
            draw.line([y_axis_start, y_axis_end], fill=(0, 0, 255, 255), width=2)  # 蓝色Y轴
            
            # 添加坐标轴标签
            axis_label_x = "X-axis"
            axis_label_y = "Y-axis"
            origin_label = "Origin(0,0)"
            
            # 如果使用摄像机作为原点，更新标签文本
            if use_camera_as_origin and camera_coords:
                axis_label_x = "Camera X-axis"
                axis_label_y = "Camera Y-axis"
                origin_label = "Camera Position"
            
            draw.text((x_axis_end[0] + 5, x_axis_end[1] - 15), axis_label_x, fill=(255, 0, 0, 255))
            draw.text((y_axis_end[0] + 5, y_axis_end[1] - 15), axis_label_y, fill=(0, 0, 255, 255))
            
            # 绘制原点
            origin = map_point((0, 0))
            draw.ellipse([(origin[0] - 3, origin[1] - 3), (origin[0] + 3, origin[1] + 3)], fill=(0, 0, 0, 255))
            draw.text((origin[0] + 5, origin[1] + 5), origin_label, fill=(0, 0, 0, 255))
            
            # 绘制曲线和标记点（如果需要）
            if len(curve_points) > 1:
                mapped_points = [map_point(p) for p in curve_points]
                # 使用较细的线条以获得更清晰的曲线轮廓
                draw.line(mapped_points, fill=(0,0,0), width=2)
                
                # 标记曲线上的点及其相对于摄像机的坐标
                # 为了避免标记过多，我们只标记采样点
                sample_interval = max(1, len(curve_points) // 20)  # 根据曲线长度决定采样间隔
                
                for i in range(0, len(curve_points), sample_interval):
                    curve_x, curve_y = curve_points[i]
                    mapped_x, mapped_y = mapped_points[i]
                    
                    # 标记点
                    draw.ellipse([(mapped_x - 3, mapped_y - 3), 
                                 (mapped_x + 3, mapped_y + 3)], 
                                fill=(0, 255, 0, 255),  # 绿色点
                                outline=(0, 0, 0, 255),  # 黑色边框
                                width=1)
                    
                    # 添加坐标标签
                    # 计算点相对于摄像机的坐标（在摄像机坐标系下）
                    if use_camera_as_origin and camera_coords:
                        # 已经是摄像机坐标系
                        rel_x, rel_y = curve_x, curve_y
                    else:
                        # 转换到摄像机坐标系
                        rel_x = curve_x - (camera_coords.x if camera_coords else 0)
                        rel_y = curve_y - (camera_coords.y if camera_coords else 0)
                    
                    # 格式化坐标文本
                    coord_text = f"({rel_x:.2f}, {rel_y:.2f})"
                    
                    # 确定标签位置，避免与其他元素重叠
                    label_offset = 15
                    label_x = mapped_x + label_offset
                    label_y = mapped_y - label_offset
                    
                    # 检查标签是否超出图像边界，如果是则调整位置
                    if label_x + 100 > img_width:
                        label_x = mapped_x - 115  # 移到左侧
                    if label_y < 15:
                        label_y = mapped_y + 15   # 移到下方
                    
                    # 绘制标签背景矩形，提高可读性
                    draw.rectangle([(label_x - 3, label_y - 12), 
                                   (label_x + 95, label_y + 5)], 
                                  fill=(255, 255, 255, 255), 
                                  outline=(0, 0, 0, 255), 
                                  width=1)
                    
                    # 绘制坐标文本
                    draw.text((label_x, label_y - 12), coord_text, fill=(0, 0, 0, 255))
            
            # 如果提供了摄像机坐标，在图上标记摄像机位置
            if camera_coords:
                # 在摄像机坐标系下，摄像机位置始终是原点(0,0)
                if use_camera_as_origin:
                    camera_xy = (0, 0)  # 摄像机坐标系下摄像机位置是原点
                else:
                    camera_xy = (camera_coords.x, camera_coords.y)  # 世界坐标系下的摄像机位置
                
                mapped_camera = map_point(camera_xy)
                
                # 确保摄像机标记在图像范围内
                # 限制摄像机标记的位置在图像的安全边界内
                safe_margin = 40
                mapped_camera = (
                    max(safe_margin, min(img_width - safe_margin, mapped_camera[0])),
                    max(safe_margin, min(img_height - safe_margin, mapped_camera[1]))
                )
                
                # Draw camera position - EXTRA visible marker
                # 1. 绘制一个更大的背景圆圈，使用更醒目的颜色
                camera_radius_bg = 25  # 显著增加大小
                draw.ellipse(
                    [(mapped_camera[0] - camera_radius_bg, mapped_camera[1] - camera_radius_bg),
                     (mapped_camera[0] + camera_radius_bg, mapped_camera[1] + camera_radius_bg)],
                    fill=(255, 255, 0, 255),  # 黄色背景
                    outline=(0, 0, 0, 255),    # 黑色边框
                    width=4                    # 更粗的边框
                )
                
                # 2. 绘制一个更大的红色中心点，确保明显可见
                camera_radius_center = 10
                draw.ellipse(
                    [(mapped_camera[0] - camera_radius_center, mapped_camera[1] - camera_radius_center),
                     (mapped_camera[0] + camera_radius_center, mapped_camera[1] + camera_radius_center)],
                    fill=(255, 0, 0, 255)  # 红色中心点
                )
                
                # 3. 添加十字线标记，进一步增强可见性
                cross_size = 30
                draw.line([(mapped_camera[0] - cross_size, mapped_camera[1]), 
                           (mapped_camera[0] + cross_size, mapped_camera[1])], 
                          fill=(0, 0, 255, 255), width=3)  # 蓝色水平线
                draw.line([(mapped_camera[0], mapped_camera[1] - cross_size), 
                           (mapped_camera[0], mapped_camera[1] + cross_size)], 
                          fill=(0, 0, 255, 255), width=3)  # 蓝色垂直线
                
                # 4. 确定标签位置 - 使用固定位置，确保在图像右下角
                label_x = img_width - 150  # 固定在右侧
                label_y = img_height - 120  # 固定在底部
                
                # 5. 绘制连接线到标签（从摄像机标记到底部标签）
                mid_x = (mapped_camera[0] + label_x + 60) // 2
                draw.line([mapped_camera, (mapped_camera[0], img_height - 50)], 
                          fill=(0, 0, 0, 255), width=3)
                draw.line([(mapped_camera[0], img_height - 50), (label_x + 60, img_height - 50)], 
                          fill=(0, 0, 0, 255), width=3)
                draw.line([(label_x + 60, img_height - 50), (label_x + 60, label_y + 70)], 
                          fill=(0, 0, 0, 255), width=3)
                
                # 6. 绘制更大、更醒目的标签背景矩形
                label_width = 140
                label_height = 110
                label_rect = [(label_x - 5, label_y - 5), 
                             (label_x + label_width, label_y + label_height)]
                draw.rectangle(label_rect, fill=(255, 255, 255, 255), 
                              outline=(0, 0, 0, 255), width=3)  # 更粗的边框
                
                # 7. 添加非常明显的标签文本，使用更大的字体大小
                draw.text((label_x, label_y), "CAMERA POSITION", fill=(255, 0, 0, 255))
                draw.text((label_x, label_y + 30), 
                         f"X: {camera_coords.x:.2f}", fill=(0, 0, 0, 255))
                draw.text((label_x, label_y + 55), 
                         f"Y: {camera_coords.y:.2f}", fill=(0, 0, 0, 255))
                draw.text((label_x, label_y + 80), 
                         f"Z: {camera_coords.z:.2f}", fill=(0, 0, 0, 255))
                
                # 8. 特别强调摄像机位置文字
                position_text = "ORIGIN" if use_camera_as_origin else "CAMERA"
                draw.text((mapped_camera[0] - 30, mapped_camera[1] - 50), 
                         position_text, fill=(255, 0, 0, 255))
        
        image.save(output_path, 'PNG')
        print(f"曲线结构已绘制并保存到: {output_path}")
        return output_path
    except Exception as e:
        print(f"绘图失败: {e}")
        return None

# 保留原有的绘图函数以确保兼容性，但不推荐使用
def draw_curve_with_points(curve_object, subdivision_points, output_file=None, camera_coords=None):
    """
    兼容性函数：调用新的曲线绘制函数
    
    参数:
        curve_object: 要绘制的曲线对象
        subdivision_points: 细分点（兼容旧接口）
        output_file: 可选，输出文件名
        camera_coords: 可选，摄像机世界坐标
    """
    return draw_curve_structure_only(curve_object, output_file, camera_coords)

# 移除渲染函数，使用PIL绘图替代

def collect_curve_info(curve_object):
    """
    Collect basic curve information
    """
    print(f"Curve name: {curve_object.name}")
    print(f"Number of splines: {len(curve_object.data.splines)}")
    if curve_object.data.splines:
        print(f"Curve type: {curve_object.data.splines[0].type}")
    return


# Removed unnecessary helper functions to keep code concise

# Main function, only draw curve structure
def main(target_curve_name=None, camera_coords=None, camera_name=None, use_camera_as_origin=False):
    """
    Main function: Draw curve structure
    
    Parameters:
        target_curve_name: Optional, specify the name of the curve object to process. If not provided, process all curve objects
        camera_coords: Optional, camera world coordinates (Vector), if provided, will mark camera position on the image
        camera_name: Optional, camera object name. If provided, will get coordinates of this camera from the scene
        use_camera_as_origin: Optional, whether to use camera coordinates as origin (0,0,0) for drawing, default is False
    
    使用示例:
        # 处理场景中所有曲线
        >>> main()
        
        # 处理特定名称的曲线
        >>> main("MyCurve")  # 将"MyCurve"替换为您场景中实际的曲线对象名称
        
        # 处理特定曲线并通过名称指定摄像机
        >>> main("MyCurve", camera_name="Camera")  # 使用场景中名为"Camera"的摄像机
        
        # 处理特定曲线并直接指定摄像机坐标
        >>> from mathutils import Vector
        >>> main("MyCurve", Vector((10, 5, 3)))  # 指定摄像机坐标为(10,5,3)
        
        # 在摄像机坐标系下绘制曲线（摄像机位置作为原点）
        >>> main("MyCurve", camera_name="Camera", use_camera_as_origin=True)
    
    重要说明:
        - 如果提供了摄像机名称或坐标，将在生成的图像中以黄色圆圈标记并显示坐标值
        - 当use_camera_as_origin=True时，所有曲线坐标将相对于摄像机位置进行变换
        - 所有绘图都是基于曲线的数学定义直接生成的
    """
    import bpy
    
    # 查找场景中的曲线对象
    all_curve_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE']
    
    # 根据是否提供target_curve_name决定处理哪些曲线
    if target_curve_name:
        # 查找特定名称的曲线
        curve_objects = [obj for obj in all_curve_objects if obj.name == target_curve_name]
        if not curve_objects:
            print(f"未找到名称为'{target_curve_name}'的曲线对象")
            print(f"可用的曲线对象有: {[obj.name for obj in all_curve_objects]}")
            return
    else:
        # 处理所有曲线
        curve_objects = all_curve_objects
    
    if not curve_objects:
        print("场景中未找到曲线对象")
        return
    
    print("Starting to draw curve structure...\n")
    print("Note: This program only draws the curve structure, not showing any punctuation or control points")
    print("Note: The current version supports marking camera position on the image through camera name or coordinates")
    if use_camera_as_origin:
        print("Note: Currently using camera coordinates as origin (0,0,0) for drawing\n")
    else:
        print("\n")
    
    # 处理摄像机坐标
    if camera_name:
        camera = bpy.data.objects.get(camera_name)
        if camera:
            camera_coords = camera.location
            print(f"从场景获取摄像机 '{camera_name}' 的坐标: X={camera_coords.x:.2f}, Y={camera_coords.y:.2f}, Z={camera_coords.z:.2f}")
        else:
            print(f"警告：未找到名称为 '{camera_name}' 的摄像机对象")
            camera_coords = None
    
    # 处理每个曲线对象
    for curve_obj in curve_objects:
        print(f"处理曲线: {curve_obj.name}")
        
        # 收集曲线信息
        collect_curve_info(curve_obj)
        
        # 打印摄像机信息（如果提供）
        if camera_coords:
            print(f"摄像机坐标: X={camera_coords.x:.2f}, Y={camera_coords.y:.2f}, Z={camera_coords.z:.2f}")
            
            # Save 2000 points on the curve relative to camera position to JSON file
            json_file = f"curve_points_{curve_obj.name}.json"
            try:
                json_path = save_curve_points_to_json(curve_obj, camera_coords, json_file)
                if json_path:
                    print(f"  - Saved points on the curve relative to camera position to JSON file: {json_path}")
            except Exception as e:
                print(f"  - Failed to save JSON file: {str(e)}")
        
        # 按曲线类型分别处理并保存图像
        output_file = f"curve_structure_{curve_obj.name}.png"
        try:
            # 直接调用新的曲线绘制函数，传递摄像机坐标和原点设置
            image_path = draw_curve_structure_only(curve_obj, output_file, camera_coords, use_camera_as_origin)
            if image_path:
                print(f"  - 曲线结构图像已保存到: {image_path}")
                if camera_coords:
                    print(f"  - 摄像机位置已在图像上标记")
            if use_camera_as_origin:
                print(f"  - 曲线以摄像机坐标系绘制（摄像机位置为原点）")
        except Exception as e:
            print(f"  - 绘制图像失败: {str(e)}")
        
        print()  # 添加空行分隔不同曲线
    
    print("All curve structures drawn")
        print("Tip: Generated images are saved in the specified folder: c:\Users\华为\Desktop\bltopo\blender_curve_subdivision")

# Support for directly specifying curve name
def process_specific_curve(curve_name, camera_coords=None, camera_name=None, use_camera_as_origin=False):
    """
    Process curve object with specified name
    
    Parameters:
        curve_name: Name of the curve object to process
        camera_coords: Optional, camera world coordinates (Vector), if provided, will mark camera position on the image
        camera_name: Optional, camera object name. If provided, will get coordinates of this camera from the scene
        use_camera_as_origin: Optional, whether to use camera coordinates as origin (0,0,0) for drawing, default is False
    
    使用示例:
        >>> process_specific_curve("MySpecialCurve")  # 将"MySpecialCurve"替换为您场景中实际的曲线对象名称
        
        # 通过名称指定摄像机
        >>> process_specific_curve("MySpecialCurve", camera_name="Camera")  # 使用场景中名为"Camera"的摄像机
        
        # 指定摄像机坐标
        >>> from mathutils import Vector
        >>> process_specific_curve("MySpecialCurve", Vector((10, 5, 3)))  # 添加摄像机坐标
        
        # 在摄像机坐标系下绘制曲线
        >>> process_specific_curve("MySpecialCurve", camera_name="Camera", use_camera_as_origin=True)
    """
    return main(target_curve_name=curve_name, camera_coords=camera_coords, camera_name=camera_name, use_camera_as_origin=use_camera_as_origin)

def save_curve_points_to_json(curve_object, camera_coords, output_file=None, num_samples=2000):
    """
    Sample points on the curve and save points relative to camera position to JSON file
    
    Parameters:
        curve_object: The curve object to process
        camera_coords: Camera world coordinates (Vector)
        output_file: Optional, output file name
        num_samples: Number of sampling points, default is 2000
    
    Returns:
        Path of the saved JSON file
    """
    # Use user-specified folder path - use raw string format to avoid Unicode escape errors
    output_dir = r"..\curve_json"
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if output_file:
        output_path = os.path.join(output_dir, output_file)
    else:
        output_path = os.path.join(output_dir, f"curve_points_{curve_object.name}.json")
    
    # 简化数据结构，只存储相对于摄像机的位置信息
    # 格式为: [ [rel_x1, rel_y1, rel_z1], [rel_x2, rel_y2, rel_z2], ... ]
    camera_relative_points = []
    
    world_matrix = curve_object.matrix_world
    total_points_collected = 0
    
    # 根据曲线类型进行采样
    for spline in curve_object.data.splines:
        if spline.type == 'BEZIER':
            # 贝塞尔曲线采样
            point_count = len(spline.bezier_points)
            segments = range(point_count if spline.use_cyclic_u else point_count - 1)
            
            # 计算每段贝塞尔曲线需要的采样点数
            points_per_segment = max(1, num_samples // max(1, len(segments)))
            
            for i in segments:
                # 获取当前点和下一个点
                p1 = spline.bezier_points[i]
                p2 = spline.bezier_points[(i + 1) % point_count] if spline.use_cyclic_u else spline.bezier_points[i + 1]
                
                # 获取控制点并应用世界变换
                p0 = world_matrix @ p1.co
                h0 = world_matrix @ p1.handle_right
                h1 = world_matrix @ p2.handle_left
                p3 = world_matrix @ p2.co
                
                # 对每个段进行采样
                for j in range(points_per_segment + 1):
                    if total_points_collected >= num_samples:
                        break
                        
                    t = j / points_per_segment
                    
                    # 计算贝塞尔曲线上的点
                    point = bezier_point(p0, h0, h1, p3, t)
                    
                    # 计算相对于摄像机的位置
                    rel_x = point.x - camera_coords.x
                    rel_y = point.y - camera_coords.y
                    rel_z = point.z - camera_coords.z
                    
                    # 只添加相对于摄像机的坐标
                    camera_relative_points.append([rel_x, rel_y, rel_z])
                    
                    total_points_collected += 1
                
                if total_points_collected >= num_samples:
                    break
                    
        elif spline.type == 'NURBS':
            # NURBS曲线采样
            # 计算需要的采样点数
            if total_points_collected < num_samples:
                remaining_points = num_samples - total_points_collected
                
                for j in range(remaining_points + 1):
                    if total_points_collected >= num_samples:
                        break
                        
                    t = j / remaining_points
                    point = evaluate_nurbs_curve(spline, t, world_matrix)
                    
                    # 计算相对于摄像机的位置
                    rel_x = point.x - camera_coords.x
                    rel_y = point.y - camera_coords.y
                    rel_z = point.z - camera_coords.z
                    
                    # 只添加相对于摄像机的坐标
                    camera_relative_points.append([rel_x, rel_y, rel_z])
                    
                    total_points_collected += 1
        
        if total_points_collected >= num_samples:
            break
    
    # 保存到JSON文件 - 只包含相对于摄像机的位置信息
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(camera_relative_points, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(camera_relative_points)} points on the curve relative to camera position to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Failed to save JSON file: {str(e)}")
        return None

# 实用函数：列出场景中所有可用的曲线对象
def list_available_curves():
    """
    列出场景中所有可用的曲线对象名称
    方便用户查找要处理的曲线名称
    
    返回:
        包含所有曲线对象名称的列表
    """
    import bpy
    curve_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE']
    curve_names = [obj.name for obj in curve_objects]
    
    if curve_names:
        print("场景中的可用曲线对象:")
        for i, name in enumerate(curve_names, 1):
            print(f"  {i}. {name}")
    else:
        print("场景中没有找到曲线对象")
    
    return curve_names

# 当脚本直接运行时执行主函数
if __name__ == "__main__":
    # 当脚本作为独立程序运行时，使用用户提供的默认值
    # 曲线名字叫"贝塞尔曲线.001",摄像机名字叫"摄像机.004"
    # 设置use_camera_as_origin=True，以摄像机位置作为原点进行绘制
    # 自动标记曲线上各点相对于摄像机的坐标
    main(target_curve_name="贝塞尔曲线.001", camera_name="摄像机.004", use_camera_as_origin=True)


# Configuration Instructions and Usage Guide:
# 1. This version focuses on visualizing the curve structure, not showing subdivision points or control points
# 2. Supports both Bezier and NURBS curve types, and uses appropriate methods to draw smooth curves
# 3. How to specify curve name (in Blender console or script):
#    - Method 1: Call main("Your curve name")
#    - Method 2: Call process_specific_curve("Your curve name")
#    - Method 3: Call main() without specifying a name to process all curves
# 4. Finding curve names:
#    - Method 1: Check the curve object name in the Blender interface
#    - Method 2: Call the list_available_curves() function to list all available curves
# 5. Camera coordinate marking feature:
#    - Can specify camera by name: main("Curve name", camera_name="Camera name")
#    - Can directly provide camera coordinates: main("Curve name", Vector((10, 5, 3)))
#    - The camera position will be marked with a red dot on the image and display specific coordinate values
# 6. Generated images are saved in the specified folder: c:\\Users\\华为\\Desktop\\bltopo\\blender_curve_subdivision, with filenames starting with 'curve_structure_'
# 7. The curve quality and drawing precision can be adjusted by modifying parameters in the draw_curve_structure_only function

# Quick Usage Examples:
# >>> import bpy
# >>> from mathutils import Vector
# >>> # After importing this script
# >>> list_available_curves()  # First check available curve names
# >>> 
# >>> # Basic usage - only draw curve structure
# >>> main("Your curve name")  # Replace with the actual curve name
# >>> 
# >>> # Add camera marking by camera name and save points on the curve relative to camera position to JSON file
# >>> main("Your curve name", camera_name="Camera name")  # Use the camera in the scene
# >>> # Or use the process_specific_curve function
# >>> process_specific_curve("Your curve name", camera_name="Camera name")
# >>> 
# >>> # Directly specify camera coordinates
# >>> main("Your curve name", Vector((10, 5, 3)))  # Add camera coordinate marking and save JSON data
# >>> process_specific_curve("Your curve name", Vector((10, 5, 3)))
# >>>
# >>> # Call the function to save curve points to JSON separately
# >>> curve_obj = bpy.data.objects["Your curve name"]
# >>> camera_coords = Vector((10, 5, 3))  # Or get from the scene
# >>> save_curve_points_to_json(curve_obj, camera_coords, "my_custom_output.json", num_samples=2000)