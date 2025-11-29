import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os
from math import sin, acos, sqrt, pi

# Configure matplotlib settings
plt.rcParams['font.sans-serif'] = ['SimHei']  # To display Chinese labels properly
plt.rcParams['axes.unicode_minus'] = False  # To display negative signs properly

class CurveDistortionAnalyzer:
    """
    Curve Distortion Analyzer for analyzing distortion conditions at each point on a curve and calculating subdivision counts
    Based on the rule: For a curved surface with the same curvature, the part where the line AB (connecting the point to its curvature center)
    is closer to being perpendicular to the line AC (connecting the point to the viewpoint) is more prone to distortion effects
    ∠BAC = α, N=6+64sin(α)
    """
    
    def __init__(self, json_file=None):
        """
        Initialize the analyzer
        
        Parameters:
            json_file: Path to JSON file containing curve points, curvature centers, and viewpoint position
        """
        self.json_file = json_file
        self.curve_points = []  # Points on the curve [(x1,y1,z1), (x2,y2,z2), ...]
        self.curvature_centers = []  # Corresponding curvature centers [(x1,y1,z1), (x2,y2,z2), ...]
        self.viewpoint = None  # Viewpoint position (x,y,z)
        self.alphas = []  # Alpha angles for each point (in radians)
        self.subdivision_counts = []  # Subdivision counts N for each point
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Set output directory to 'test_results' folder at the same level
        self.output_dir = os.path.join(script_dir, "test_results")
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 如果提供了JSON文件，加载数据
        if json_file:
            self.load_data_from_json()
    
    def calculate_curvature_center(self, prev_point, current_point, next_point):
        """
        Calculate the curvature center at the current point based on three points
        Uses the three-point circle determination method to estimate the curvature center
        
        Parameters:
            prev_point: Previous point to the current point
            current_point: Current point
            next_point: Next point after the current point
            
        Returns:
            Curvature center coordinates [x, y, z]
        """
        try:
            # 将点转换为numpy数组
            p0 = np.array(prev_point)
            p1 = np.array(current_point)
            p2 = np.array(next_point)
            
            # 计算向量
            v0 = p1 - p0
            v1 = p2 - p1
            
            # 计算法向量（垂直于v0和v1）
            normal = np.cross(v0, v1)
            
            # Avoid zero vector case
            if np.linalg.norm(normal) < 1e-6:
                # If three points are approximately collinear, determine curvature center using direction perpendicular to curve
                # Using a simplified method here, extending along the direction perpendicular to curve tangent
                if np.linalg.norm(v0) > 1e-6:
                    # Calculate unit vector in tangent direction
                    tangent = v0 / np.linalg.norm(v0)
                    # Create a perpendicular direction (simplified treatment)
                    # For 2D case, we can use 90-degree rotation
                    # For 3D case, we need a vector perpendicular to tangent
                    # Choosing a simple perpendicular direction here
                    if abs(tangent[0]) > abs(tangent[1]):
                        perpendicular = np.array([-tangent[1], tangent[0], 0])
                    else:
                        perpendicular = np.array([0, -tangent[0], tangent[1]])
                    
                    # Ensure perpendicular vector is not zero
                    if np.linalg.norm(perpendicular) < 1e-6:
                        perpendicular = np.array([0, 0, 1])  # Default to z-axis direction
                    
                    perpendicular = perpendicular / np.linalg.norm(perpendicular)
                    
                    # Return a point along perpendicular direction as curvature center (simplified)
                    # In practical applications, should calculate based on curvature radius
                    return p1 + perpendicular * 1.0  # Using fixed distance here, should calculate curvature radius in practice
                return p1  # If calculation is impossible, return current point
            
            # 归一化法向量
            normal = normal / np.linalg.norm(normal)
            
            # 计算三角形的外接圆中心
            # 解方程组 (p - p0)·(p0 - p1) = |p0|²/2 - |p1|²/2
            # (p - p0)·(p0 - p2) = |p0|²/2 - |p2|²/2
            # 由于我们在3D空间中，需要使用另外的方法
            # 这里使用最小二乘法求解最佳拟合圆
            
            # Simplified approach: Use center in the direction perpendicular to v0 and v1
            # In practical applications, should use more precise methods to calculate curvature center
            
            # Calculate normal plane of three points
            # Curvature center lies on the plane passing through p1 and perpendicular to curve tangent
            
            # Simplified approach: Return a reasonable estimate of curvature center
            # This is just an approximation, precise curvature center calculation should be used in practical applications
            
            # Using a simplified method here: Find the point equidistant from three points
            # Since this is an approximation, we perform calculation only in 2D plane
            # Extract x and y coordinates for calculation
            x0, y0, _ = p0
            x1, y1, _ = p1
            x2, y2, _ = p2
            
            # 解方程组 (x - x0)² + (y - y0)² = (x - x1)² + (y - y1)²
            # (x - x1)² + (y - y1)² = (x - x2)² + (y - y2)²
            
            # 简化为线性方程
            A = np.array([
                [2*(x1 - x0), 2*(y1 - y0)],
                [2*(x2 - x1), 2*(y2 - y1)]
            ])
            
            b = np.array([
                x1**2 + y1**2 - x0**2 - y0**2,
                x2**2 + y2**2 - x1**2 - y1**2
            ])
            
            # Check if matrix is invertible
            if np.linalg.det(A) != 0:
                # Solve linear system
                solution = np.linalg.solve(A, b)
                x_center, y_center = solution
                
                # Use z-coordinate of p1 as z-coordinate of center
                z_center = p1[2]
                
                # Calculate curvature center
                center_2d = np.array([x_center, y_center, z_center])
                
                # Ensure curvature center is at a reasonable position
                # If too far from current point, use simplified method
                if np.linalg.norm(center_2d - p1) > 100:  # Threshold can be adjusted as needed
                    # Use simplified method
                    if np.linalg.norm(v0) > 1e-6:
                        tangent = v0 / np.linalg.norm(v0)
                        if abs(tangent[0]) > abs(tangent[1]):
                            perpendicular = np.array([-tangent[1], tangent[0], 0])
                        else:
                            perpendicular = np.array([0, -tangent[0], tangent[1]])
                        
                        if np.linalg.norm(perpendicular) < 1e-6:
                            perpendicular = np.array([0, 0, 1])
                        
                        perpendicular = perpendicular / np.linalg.norm(perpendicular)
                        return p1 + perpendicular * 1.0
                    return p1
                
                return center_2d
            else:
                # If three points are collinear or nearly collinear, use simplified method
                if np.linalg.norm(v0) > 1e-6:
                    tangent = v0 / np.linalg.norm(v0)
                    if abs(tangent[0]) > abs(tangent[1]):
                        perpendicular = np.array([-tangent[1], tangent[0], 0])
                    else:
                        perpendicular = np.array([0, -tangent[0], tangent[1]])
                    
                    if np.linalg.norm(perpendicular) < 1e-6:
                        perpendicular = np.array([0, 0, 1])
                    
                    perpendicular = perpendicular / np.linalg.norm(perpendicular)
                    return p1 + perpendicular * 1.0
                return p1
        except Exception as e:
            print(f"Error calculating curvature center: {e}")
            return current_point
    
    def calculate_curvature_2d(self, prev_point, current_point, next_point):
        """
        Calculate the curvature of a point on a 2D curve
        
        Args:
            prev_point: Previous point of the current point [x, y]
            current_point: Current point [x, y]
            next_point: Next point of the current point [x, y]
            
        Returns:
            Curvature value (1/radius)
        """
        try:
            # Convert points to numpy arrays
            p0 = np.array(prev_point[:2])  # Take only first two coordinates
            p1 = np.array(current_point[:2])
            p2 = np.array(next_point[:2])
            
            # Calculate vectors
            v1 = p1 - p0
            v2 = p2 - p1
            
            # Calculate vector lengths
            len_v1 = np.linalg.norm(v1)
            len_v2 = np.linalg.norm(v2)
            
            # Avoid division by zero
            if len_v1 < 1e-6 or len_v2 < 1e-6:
                return 0
            
            # Calculate unit vectors
            u1 = v1 / len_v1
            u2 = v2 / len_v2
            
            # Calculate change in tangent direction (angle change)
            # Use vector dot product to calculate angle
            dot_product = np.dot(u1, u2)
            
            # Clamp within [-1,1] range
            dot_product = max(min(dot_product, 1.0), -1.0)
            
            # Calculate angle change
            delta_theta = np.arccos(dot_product)
            
            # Calculate arc length (using average distance between points)
            arc_length = (len_v1 + len_v2) / 2
            
            # Avoid division by zero
            if arc_length < 1e-6:
                return 0
            
            # Calculate curvature = angle change / arc length
            curvature = delta_theta / arc_length
            
            return curvature
            
        except Exception as e:
            print(f"Error calculating curvature: {e}")
            return 0


    

        
        # 计算所有点的曲率中心
        self.calculate_all_curvature_centers()
        
        # 计算所有点的alpha角
        alphas = []
        sin_alphas = []
        valid_indices = []
        
        for i in range(len(self.curve_points)):
            if i < len(self.curvature_centers):
                point = self.curve_points[i]
                center = self.curvature_centers[i]
                
                # 计算alpha角
                alpha = self.calculate_alpha(point, center, self.viewpoint)
                alphas.append(alpha)
                sin_alphas.append(np.sin(alpha))
                valid_indices.append(i)
        
        print(f"计算了 {len(alphas)} 个alpha角值")
        
        # 绘制alpha正弦值图
        plt.figure(figsize=(10, 6))
        
        x_valid = [x_range[i] for i in valid_indices]
        
        # 绘制sin(alpha)随x坐标的变化
        plt.plot(x_valid, sin_alphas, 'bo-', markersize=3, linewidth=1)
        plt.xlabel('')
        plt.ylabel('')
        plt.title('')

    
    def calculate_curvature_radius_2d(self, prev_point, current_point, next_point):
        """
        Calculate the curvature radius of a point on a 2D curve
        
        Args:
            prev_point: Previous point of the current point [x, y]
            current_point: Current point [x, y]
            next_point: Next point of the current point [x, y]
            
        Returns:
            Curvature radius
        """
        curvature = self.calculate_curvature_2d(prev_point, current_point, next_point)
        
        # Avoid division by zero
        if abs(curvature) < 1e-6:
            return float('inf')  # Curvature radius of a straight line is infinite
        
        return 1.0 / curvature
    
    def calculate_curvature_center_from_curvature(self, point, curvature_radius, tangent_direction):
        """
        Calculate curvature center based on curvature radius and tangent direction
        
        Args:
            point: Current point [x, y]
            curvature_radius: Curvature radius
            tangent_direction: Tangent direction vector [dx, dy]
            
        Returns:
            Curvature center [x, y]
        """
        try:
            # Normalize tangent direction
            tangent_norm = np.linalg.norm(tangent_direction)
            if tangent_norm < 1e-6:
                return point
            
            tangent_unit = tangent_direction / tangent_norm
            
            # Calculate normal direction (perpendicular to tangent)
            # In 2D, normal direction can be obtained by rotating tangent 90 degrees
            normal = np.array([-tangent_unit[1], tangent_unit[0]])
            
            # Curvature center = current point + curvature radius * normal direction
            curvature_center = point + curvature_radius * normal
            
            return curvature_center
            
        except Exception as e:
            print(f"Error calculating curvature center from curvature: {e}")
            return point
    
    def demonstrate_curvature_calculation(self, point_index):
        """
        Demonstrate how to calculate curvature and related parameters for a point on a curve
        
        Args:
            point_index: Index of the point to analyze
        """
        if len(self.curve_points) < 3:
            print("Error: Insufficient curve points for curvature calculation demonstration")
            return
        
        # Ensure index is within valid range
        if point_index < 1 or point_index >= len(self.curve_points) - 1:
            print("Error: Invalid point index, please select a middle point (1 to n-2)")
            return
        
        # Get three points
        prev_point = self.curve_points[point_index - 1]
        current_point = self.curve_points[point_index]
        next_point = self.curve_points[point_index + 1]
        
        print(f"=== Curvature Calculation Demonstration (Point {point_index}) ===")
        print(f"Previous point: {prev_point}")
        print(f"Current point: {current_point}")
        print(f"Next point: {next_point}")
        
        # Calculate curvature
        curvature = self.calculate_curvature_2d(prev_point, current_point, next_point)
        curvature_radius = self.calculate_curvature_radius_2d(prev_point, current_point, next_point)
        
        print(f"Curvature: {curvature:.6f}")
        print(f"Curvature radius: {curvature_radius:.6f}")
        
        # Calculate tangent direction
        v1 = np.array(current_point[:2]) - np.array(prev_point[:2])
        v2 = np.array(next_point[:2]) - np.array(current_point[:2])
        tangent_direction = (v1 + v2) / 2  # Average tangent direction
        
        # Calculate curvature center based on curvature
        if curvature_radius != float('inf'):
            curvature_center = self.calculate_curvature_center_from_curvature(
                np.array(current_point[:2]), curvature_radius, tangent_direction
            )
            print(f"Curvature center calculated from curvature: {curvature_center}")
        
        # Calculate curvature center using three-point circle method
        circle_center = self.calculate_curvature_center(prev_point, current_point, next_point)
        print(f"Curvature center calculated by three-point circle method: {circle_center}")
        
        # 计算alpha角（如果视点存在）
        if self.viewpoint is not None:
            alpha = self.calculate_alpha(current_point, circle_center, self.viewpoint)
            print(f"α角: {alpha:.6f} 弧度 ({alpha * 180/np.pi:.2f}°)")
            
            # 计算细分点数
            n = self.calculate_subdivision_count(alpha)
            print(f"细分点数 N: {n:.2f}")
        
        print("=" * 50)
    
    def calculate_all_curvature_centers(self):
        """
        Calculate curvature centers for all curve points
        """
        if len(self.curve_points) < 3:
            print("Warning: Number of curve points is less than 3, cannot calculate curvature centers")
            # If there are too few points, use a simplified method
            self.curvature_centers = [p.copy() for p in self.curve_points]
            return
        
        self.curvature_centers = []
        
        # Process the first point (using the first three points)
        center = self.calculate_curvature_center(self.curve_points[0], self.curve_points[1], self.curve_points[2])
        self.curvature_centers.append(center)
        
        # Process middle points
        for i in range(1, len(self.curve_points) - 1):
            center = self.calculate_curvature_center(self.curve_points[i-1], self.curve_points[i], self.curve_points[i+1])
            self.curvature_centers.append(center)
        
        # Process the last point (using the last three points)
        center = self.calculate_curvature_center(self.curve_points[-3], self.curve_points[-2], self.curve_points[-1])
        self.curvature_centers.append(center)
        
        print(f"Calculated {len(self.curvature_centers)} curvature centers")
    
    def load_data_from_json(self):
        """
        Load curve points, curvature centers, and viewpoint position data from JSON file
        Supports two formats:
        1. Complete format: Contains 'curve_points', 'curvature_centers', and 'viewpoint' fields
        2. Simplified format: Directly a 2D array representing points relative to the camera
        """
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's simplified format (directly a 2D array)
            if isinstance(data, list) and data and isinstance(data[0], list) and len(data[0]) == 3:
                print("Detected simplified format JSON file (containing only position information relative to camera)")
                
                # Convert simplified format to data required for complete format
                # Assume camera position is at origin [0, 0, 0] since data is already relative to camera
                self.viewpoint = [0, 0, 0]
                print(f"Assuming camera position at origin: {self.viewpoint}")
                
                # Relative coordinates are the curve point positions (relative to camera coordinate system)
                self.curve_points = data
                print(f"Loaded {len(self.curve_points)} curve points (positions relative to camera)")
                
                # Calculate curvature centers (based on curve geometry, not simply using camera position)
                self.calculate_all_curvature_centers()
            
            # Complete format handling
            elif isinstance(data, dict):
                # Extract curve points
                if 'curve_points' in data:
                    self.curve_points = data['curve_points']
                    print(f"Loaded {len(self.curve_points)} curve points")
                else:
                    print("Warning: 'curve_points' field not found in JSON file")
                
                # Extract curvature centers
                if 'curvature_centers' in data:
                    self.curvature_centers = data['curvature_centers']
                    print(f"Loaded {len(self.curvature_centers)} curvature centers")
                    # Ensure the number of curvature centers matches the number of curve points
                    if len(self.curvature_centers) != len(self.curve_points):
                        print("Warning: Number of curve points does not match number of curvature centers")
                else:
                    print("Warning: 'curvature_centers' field not found in JSON file")
                
                # Extract viewpoint position
                if 'viewpoint' in data:
                    self.viewpoint = data['viewpoint']
                    print(f"Loaded viewpoint position: {self.viewpoint}")
                else:
                    print("Warning: 'viewpoint' field not found in JSON file")
            else:
                print("Error: Unsupported JSON file format, should be an object or 2D array")
            
        except Exception as e:
            print(f"Failed to load JSON file: {e}")
    
    def set_data(self, curve_points, curvature_centers, viewpoint):
        """
        Directly set data (without JSON file)
        
        Args:
            curve_points: List of points on the curve
            curvature_centers: List of curvature centers for corresponding points
            viewpoint: Viewpoint position
        """
        self.curve_points = curve_points
        self.curvature_centers = curvature_centers
        self.viewpoint = viewpoint
    
    def calculate_alpha(self, point, center, viewpoint):
        """
        Calculate ∠BAC (alpha angle), where B is the curvature center, A is the point on the curve, and C is the viewpoint
        
        Args:
            point: Point A on the curve
            center: Curvature center B
            viewpoint: Viewpoint C
            
        Returns:
            Alpha angle (in radians)
        """
        # Calculate vectors AB and AC
        vector_ab = np.array(center) - np.array(point)
        vector_ac = np.array(viewpoint) - np.array(point)
        
        # Calculate vector lengths
        len_ab = np.linalg.norm(vector_ab)
        len_ac = np.linalg.norm(vector_ac)
        
        # Avoid division by zero error
        if len_ab < 1e-6 or len_ac < 1e-6:
            return 0
        
        # Calculate dot product
        dot_product = np.dot(vector_ab, vector_ac)
        
        # Calculate angle (in radians)
        cos_alpha = dot_product / (len_ab * len_ac)
        
        # Restrict cos_alpha to [-1,1] range to avoid numerical errors
        cos_alpha = max(min(cos_alpha, 1.0), -1.0)
        
        return acos(cos_alpha)
    
    def calculate_subdivision_count(self, alpha):
        """
        Calculate the number of subdivisions N based on alpha angle
        N = 6 + 64 * sin(alpha)
        
        Args:
            alpha: Alpha angle (in radians)
            
        Returns:
            Number of subdivisions N
        """
        return 6 + 64 * sin(alpha)
    
    def analyze(self):
        """
        Analyze distortion for all points
        """
        if not self.curve_points or not self.curvature_centers or self.viewpoint is None:
            print("Error: Missing necessary data, cannot perform analysis")
            return False
        
        # Ensure data lengths match
        n_points = min(len(self.curve_points), len(self.curvature_centers))
        self.alphas = []
        self.subdivision_counts = []
        
        print(f"Starting analysis of {n_points} points...")
        
        for i in range(n_points):
            point = self.curve_points[i]
            center = self.curvature_centers[i]
            
            # Calculate alpha angle
            alpha = self.calculate_alpha(point, center, self.viewpoint)
            self.alphas.append(alpha)
            
            # Calculate subdivision count
            n = self.calculate_subdivision_count(alpha)
            self.subdivision_counts.append(n)
            
            # Print progress
            if (i + 1) % 100 == 0 or i + 1 == n_points:
                print(f"Analyzed {i + 1}/{n_points} points")
        
        print("Analysis completed")
        
        # Print statistics
        if self.alphas:
            print(f"Alpha angle range: {min(self.alphas):.4f} - {max(self.alphas):.4f} radians")
            print(f"Alpha angle range: {min(self.alphas) * 180/pi:.2f}° - {max(self.alphas) * 180/pi:.2f}°")
            print(f"Subdivision count range: {min(self.subdivision_counts):.2f} - {max(self.subdivision_counts):.2f}")
        
        return True
    
    def visualize_results(self, save_figures=True):
        """
        Visualize analysis results
        
        Args:
            save_figures: Whether to save the figures
            
        Returns:
            List of saved image paths
        """
        if not self.alphas or not self.subdivision_counts:
            print("错误: 没有分析结果可供可视化")
            return []
        
        saved_files = []
        
        # 创建可视化目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 1. 绘制α角和细分点数随曲线参数的变化（跳过，不生成curve_distortion_analysis.png）
        # 这部分代码被移除，因为用户要求不生成这张图片
        
        # 2. 绘制α角与细分点数的关系（理论曲线和实际数据点）
        plt.figure(figsize=(10, 6))
        
        # 生成理论曲线
        alpha_theory = np.linspace(0, pi/2, 100)
        n_theory = [self.calculate_subdivision_count(a) for a in alpha_theory]
        
        plt.plot(alpha_theory * 180/pi, n_theory, 'k--', linewidth=2, label='Theoretical Curve')
        plt.scatter([a * 180/pi for a in self.alphas], self.subdivision_counts, 
                   color='red', alpha=0.6, label='Actual Data Points')
        
        plt.xlabel('Alpha Angle (degrees)')
        plt.ylabel('Subdivision Count N')
        plt.title('Relationship between Alpha Angle and Subdivision Count (N = 6 + 64sin(α))')
        plt.grid(True)
        plt.legend()
        
        # 标注关键点
        plt.axhline(y=6, color='g', linestyle='-', alpha=0.5)
        plt.axhline(y=6 + 64, color='g', linestyle='-', alpha=0.5)
        plt.text(5, 6, 'N=6 (α=0°)', color='g')
        plt.text(5, 6 + 64, 'N=70 (α=90°)', color='g')
        
        if save_figures:
            file_path = os.path.join(self.output_dir, 'alpha_vs_subdivision.png')
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            saved_files.append(file_path)
            print(f"图像已保存到: {file_path}")
        
        # 3. 如果有3D坐标，绘制2D投影图，显示点、曲率中心和视点
        if self.curve_points and len(self.curve_points[0]) >= 2 and self.viewpoint:
            plt.figure(figsize=(10, 8))
            
            # 提取X-Y平面的数据
            curve_x = [p[0] for p in self.curve_points]
            curve_y = [p[1] for p in self.curve_points]
            
            # 绘制曲线
            plt.plot(curve_x, curve_y, 'b-', linewidth=2, label='Curve')
            
            # 绘制点（颜色根据α角变化）
            colors = [a for a in self.alphas]  # 使用α角作为颜色映射
            scatter = plt.scatter(curve_x, curve_y, c=colors, cmap='viridis', 
                                 s=100, alpha=0.7, label='Curve Points')
            
            # Add colorbar
            cbar = plt.colorbar(scatter)
            cbar.set_label('Alpha Angle (radians)')
            
            # Plot viewpoint
            plt.scatter(self.viewpoint[0], self.viewpoint[1], color='red', s=200, 
                       marker='*', label='Viewpoint')
            
            # Plot some curvature centers and connecting lines (to avoid overcrowding)
            step = max(1, len(self.curve_points) // 50)
            for i in range(0, len(self.curve_points), step):
                if i < len(self.curvature_centers):
                    cx, cy = self.curvature_centers[i][0], self.curvature_centers[i][1]
                    plt.plot([curve_x[i], cx], [curve_y[i], cy], 'g-', alpha=0.3)
            
            plt.xlabel('X Coordinate')
            plt.ylabel('Y Coordinate')
            plt.title('2D Projection of Curve, Viewpoint and Curvature Centers')
            plt.legend()
            plt.grid(True)
            
            # Ensure equal scale for x and y axes
            plt.axis('equal')
            # Set axis limits to center the curve
            x_range = max(curve_x) - min(curve_x)
            y_range = max(curve_y) - min(curve_y)
            max_range = max(x_range, y_range)
            
            x_center = (max(curve_x) + min(curve_x)) / 2
            y_center = (max(curve_y) + min(curve_y)) / 2
            
            padding = max_range * 0.1  # 10% padding
            plt.xlim(x_center - max_range/2 - padding, x_center + max_range/2 + padding)
            plt.ylim(y_center - max_range/2 - padding, y_center + max_range/2 + padding)
            
            # Again ensure equal scale for x and y axes
            plt.gca().set_aspect('equal', adjustable='box')
            
            if save_figures:
                file_path = os.path.join(self.output_dir, 'curve_2d_visualization.png')
                plt.savefig(file_path, dpi=300, bbox_inches='tight')
                saved_files.append(file_path)
                print(f"Image saved to: {file_path}")
        
        # 显示所有图像
        plt.show()
        
        return saved_files
    
    # generate_sample_data函数已移除，不再支持生成默认圆形数据
    
    def export_results(self, output_file=None):
        """
        Export analysis results to JSON file
        
        Args:
            output_file: Output file path, automatically generated if not provided
            
        Returns:
            Exported file path
        """
        if not self.alphas or not self.subdivision_counts:
            print("错误: 没有分析结果可供导出")
            return None
        
        # 如果没有提供输出文件路径，自动生成
        if not output_file:
            output_file = os.path.join(self.output_dir, 'distortion_analysis_results.json')
        
        # Prepare export data
        results = {
            'curve_points': self.curve_points,
            'curvature_centers': self.curvature_centers,
            'viewpoint': self.viewpoint,
            'alphas': self.alphas,
            'subdivision_counts': self.subdivision_counts,
            'statistics': {
                'min_alpha': min(self.alphas) if self.alphas else 0,
                'max_alpha': max(self.alphas) if self.alphas else 0,
                'min_subdivision_count': min(self.subdivision_counts) if self.subdivision_counts else 0,
                'max_subdivision_count': max(self.subdivision_counts) if self.subdivision_counts else 0,
                'mean_subdivision_count': np.mean(self.subdivision_counts) if self.subdivision_counts else 0
            }
        }
        
        # Export to JSON file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Analysis results exported to: {output_file}")
            return output_file
        except Exception as e:
            print(f"Failed to export results: {e}")
            return None
    
    def import_results(self, input_file):
        """
        Import previously generated analysis results file
        
        Args:
            input_file: Input file path, should be a file generated by export_results
            
        Returns:
            Whether import was successful
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Check for necessary data fields
            required_fields = ['curve_points', 'curvature_centers', 'viewpoint', 'alphas', 'subdivision_counts']
            for field in required_fields:
                if field not in results:
                    print(f"Error: Missing required field '{field}' in import file")
                    return False
            
            # Import data
            self.curve_points = results['curve_points']
            self.curvature_centers = results['curvature_centers']
            self.viewpoint = results['viewpoint']
            self.alphas = results['alphas']
            self.subdivision_counts = results['subdivision_counts']
            
            print(f"Successfully imported analysis results:")
            print(f"- Number of curve points: {len(self.curve_points)}")
            print(f"- Number of curvature centers: {len(self.curvature_centers)}")
            print(f"- Viewpoint position: {self.viewpoint}")
            print(f"- Number of alpha angles: {len(self.alphas)}")
            print(f"- Number of subdivision counts: {len(self.subdivision_counts)}")
            
            # If there are statistics, print them
            if 'statistics' in results:
                stats = results['statistics']
                print(f"\nStatistics:")
                print(f"- Minimum alpha angle: {stats.get('min_alpha', 0):.4f} radians")
                print(f"- Maximum alpha angle: {stats.get('max_alpha', 0):.4f} radians")
                print(f"- Minimum subdivision count: {stats.get('min_subdivision_count', 0):.2f}")
                print(f"- Maximum subdivision count: {stats.get('max_subdivision_count', 0):.2f}")
                print(f"- Mean subdivision count: {stats.get('mean_subdivision_count', 0):.2f}")
            
            return True
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            return False
        except json.JSONDecodeError:
            print(f"Error: File '{input_file}' is not a valid JSON format")
            return False
        except Exception as e:
            print(f"Failed to import results: {e}")
            return False

    def calculate_arc_lengths(self):
        """
        Calculate arc length parameterization for each point on the curve
        
        Returns:
            arc_lengths: List of arc lengths from the starting point to each point
            total_length: Total length of the curve
        """
        if len(self.curve_points) < 2:
            print("Error: Insufficient curve points to calculate arc lengths")
            return [], 0
        
        arc_lengths = [0.0]  # Arc length at starting point is 0
        
        # Calculate distance between adjacent points and accumulate to get arc lengths
        for i in range(1, len(self.curve_points)):
            prev_point = np.array(self.curve_points[i-1])
            current_point = np.array(self.curve_points[i])
            distance = np.linalg.norm(current_point - prev_point)
            arc_lengths.append(arc_lengths[-1] + distance)
        
        total_length = arc_lengths[-1]
        
        return arc_lengths, total_length

    def calculate_point_density(self):
        """
        Calculate point density ρ for each point on the curve
        ρ = N / (2πR), where N is the subdivision count and R is the curvature radius
        
        Returns:
            densities: List of point densities
        """
        if not self.subdivision_counts or len(self.curve_points) < 3:
            print("错误: 没有细分点数数据或曲线点数量不足")
            return []
        
        densities = []
        
        for i in range(len(self.curve_points)):
            # Get subdivision count N
            N = self.subdivision_counts[i]
            
            # Calculate curvature radius R
            if i == 0:
                # For the first point, use the first three points to calculate curvature
                curvature_radius = self.calculate_curvature_radius_2d(
                    self.curve_points[0], self.curve_points[1], self.curve_points[2]
                )
            elif i == len(self.curve_points) - 1:
                # For the last point, use the last three points to calculate curvature
                curvature_radius = self.calculate_curvature_radius_2d(
                    self.curve_points[-3], self.curve_points[-2], self.curve_points[-1]
                )
            else:
                # For middle points, use three points (previous, current, next) to calculate curvature
                curvature_radius = self.calculate_curvature_radius_2d(
                    self.curve_points[i-1], self.curve_points[i], self.curve_points[i+1]
                )
            
            # Avoid division by zero (curvature radius of a straight line is infinity)
            if curvature_radius == float('inf'):
                # For straight lines, use a large value or special handling
                density = N / (2 * np.pi * 1000)  # Use a large radius value
            else:
                # Calculate point density ρ = N / (2πR)
                density = N / (2 * np.pi * curvature_radius)
            
            densities.append(density)
        
        return densities

    def calculate_cumulative_distribution(self):
        """
        Calculate unnormalized cumulative distribution function p(t)
        p(t) = ∫₀ᵗ ρ(u) du
        
        Returns:
            p_values: List of cumulative distribution function values
            t_values: Parameterization parameter t = s/L ∈ [0,1]
        """
        # Calculate arc length parameterization
        arc_lengths, total_length = self.calculate_arc_lengths()
        if total_length == 0:
            print("Error: Curve total length is 0, cannot calculate cumulative distribution")
            return [], []
        
        # Calculate point densities
        densities = self.calculate_point_density()
        if not densities:
            print("Error: Cannot calculate point densities")
            return [], []
        
        # Calculate parameterization parameter t = s/L
        t_values = [s / total_length for s in arc_lengths]
        
        # Calculate cumulative distribution function p(t) = ∫₀ᵗ ρ(u) du
        # Use trapezoidal rule for numerical integration
        p_values = [0.0]  # p(0) = 0
        
        for i in range(1, len(t_values)):
            # Trapezoidal area = (ρ_{i-1} + ρ_i) * (t_i - t_{i-1}) / 2
            delta_t = t_values[i] - t_values[i-1]
            area = (densities[i-1] + densities[i]) * delta_t / 2
            p_values.append(p_values[-1] + area)
        
        return p_values, t_values

    def calculate_division_points(self, num_divisions=None):
        """
        Calculate division points on the curve t_k = p⁻¹(k)
        
        Args:
            num_divisions: Number of divisions, if not provided use maximum subdivision count
            
        Returns:
            division_t: List of parameterized positions of division points
            division_indices: Indices of division points in the curve points list
        """
        # Calculate cumulative distribution function
        p_values, t_values = self.calculate_cumulative_distribution()
        if not p_values:
            print("Error: Cannot calculate cumulative distribution function")
            return [], []
        
        # Determine number of divisions
        if num_divisions is None:
            # Use maximum subdivision count as number of divisions
            max_N = max(self.subdivision_counts) if self.subdivision_counts else 10
            num_divisions = int(max_N)
        
        # Calculate division points
        division_t = []
        division_indices = []
        
        # Maximum value of the cumulative distribution function
        max_p = p_values[-1]
        
        # Ensure curve start point is included (t=0)
        division_t.append(t_values[0])
        division_indices.append(0)
        
        # If the maximum value of cumulative distribution function is less than 1, need to re-understand the algorithm
        # According to theory, p(t) = ∫₀ᵗ ρ(u)du, and ρ(u) = N/(2πR)
        # Since both N and R are finite, p(t) values might be small
        # We need to normalize k values to the range of p(t)
        
        for k in range(1, num_divisions):
            # Normalize k to the range of p(t)
            # Target p value should be within the range of the cumulative distribution function
            target_p = (k / num_divisions) * max_p
            
            # Use linear interpolation to find t_k = p⁻¹(target_p)
            found = False
            for i in range(1, len(p_values)):
                if p_values[i-1] <= target_p <= p_values[i]:
                    # Linear interpolation
                    t_k = t_values[i-1] + (target_p - p_values[i-1]) * (t_values[i] - t_values[i-1]) / (p_values[i] - p_values[i-1])
                    division_t.append(t_k)
                    
                    # Find the corresponding curve point index
                    # Find the closest index
                    closest_index = min(range(len(t_values)), key=lambda j: abs(t_values[j] - t_k))
                    division_indices.append(closest_index)
                    
                    found = True
                    break
            
            if not found and target_p <= max_p:
                # If target_p is within range but no exact match found, use the last point
                division_t.append(t_values[-1])
                division_indices.append(len(t_values) - 1)
        
        # Ensure curve end point is included (t=1), using ceiling method
        # If the last division point is not the end point, add the end point
        if len(division_t) == 0 or division_t[-1] < t_values[-1]:
            division_t.append(t_values[-1])
            division_indices.append(len(t_values) - 1)
        
        return division_t, division_indices

    def visualize_division_points(self, num_divisions=None):
        """
        Visualize division point results
        
        Args:
            num_divisions: Number of divisions
        """
        # Calculate division points
        division_t, division_indices = self.calculate_division_points(num_divisions)
        
        if not division_indices:
            print("Error: Cannot calculate division points")
            return
        
        # Extract x,y coordinates of curve points
        x_coords = [point[0] for point in self.curve_points]
        y_coords = [point[1] for point in self.curve_points]
        
        # Extract coordinates of division points
        division_x = [self.curve_points[i][0] for i in division_indices]
        division_y = [self.curve_points[i][1] for i in division_indices]
        
        # Create three separate figures, each showing a subplot
        
        # Calculate point densities and cumulative distribution function
        densities = self.calculate_point_density()
        p_values, t_values = self.calculate_cumulative_distribution()
        
        # First figure: Original curve and division points
        plt.figure(figsize=(8, 6))
        plt.plot(x_coords, y_coords, 'b-', linewidth=1, label='Original Curve')
        plt.scatter(division_x, division_y, c='red', s=30, label=f'Division Points ({len(division_indices)} points)')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Curve Division Points Visualization')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save first figure
        output_file1 = os.path.join(self.output_dir, 'curve_division_points.png')
        plt.savefig(output_file1, dpi=300, bbox_inches='tight')
        print(f"Division points visualization image saved to: {output_file1}")
        plt.close()
        
        # Second figure: Point density distribution
        if densities:
            plt.figure(figsize=(8, 6))
            arc_lengths, total_length = self.calculate_arc_lengths()
            t_values_density = [s / total_length for s in arc_lengths]
            plt.plot(t_values_density, densities, 'g-', linewidth=2)
            plt.xlabel('Parameter t')
            plt.ylabel('Point Density ρ')
            plt.title('Point Density Distribution')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save second figure
            output_file2 = os.path.join(self.output_dir, 'point_density_distribution.png')
            plt.savefig(output_file2, dpi=300, bbox_inches='tight')
            print(f"Point density distribution image saved to: {output_file2}")
            plt.close()
        
        # Third figure: Cumulative distribution function
        if p_values:
            plt.figure(figsize=(8, 6))
            plt.plot(t_values, p_values, 'r-', linewidth=2, label='p(t)')
            
            # Mark division points
            for k, t_k in enumerate(division_t, 1):
                if k <= len(p_values):
                    plt.axvline(x=t_k, color='red', linestyle='--', alpha=0.5)
            
            plt.xlabel('Parameter t')
            plt.ylabel('Cumulative Distribution p(t)')
            plt.title('Cumulative Distribution Function')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save third figure
            output_file3 = os.path.join(self.output_dir, 'cumulative_distribution.png')
            plt.savefig(output_file3, dpi=300, bbox_inches='tight')
            print(f"Cumulative distribution function image saved to: {output_file3}")
            plt.close()
        
        # Display all figures
        plt.show()
        
        # Print division point information
        print(f"\nDivision point analysis results:")
        print(f"- Total division count: {len(division_indices)}")
        print(f"- Division point parameter positions: {[f'{t:.4f}' for t in division_t[:5]]}...")
        print(f"- Division point indices: {division_indices[:5]}...")
        
        if densities:
            print(f"- Point density range: {min(densities):.6f} - {max(densities):.6f}")
        
        if p_values:
            print(f"- Cumulative distribution range: {min(p_values):.4f} - {max(p_values):.4f}")

    def export_division_points(self, num_divisions=None, output_file=None):
        """
        Export division point data to a JSON file
        
        Args:
            num_divisions: Number of divisions
            output_file: Output JSON file path, automatically generated if None
            
        Returns:
            dict: Dictionary containing division point data
        """
        # Calculate division points
        division_t, division_indices = self.calculate_division_points(num_divisions)
        
        if not division_indices:
            print("Error: Unable to calculate division points")
            return None
        
        # Prepare export data
        export_data = {
            "total_divisions": len(division_indices),
            "division_points": [],
            "statistics": {}
        }
        
        # 添加每个划分点的详细信息
        for i, (t, idx) in enumerate(zip(division_t, division_indices)):
            point_data = {
                "index": i + 1,
                "parameter_t": round(t, 6),
                "point_index": idx,
                "coordinates": {
                    "x": round(self.curve_points[idx][0], 6),
                    "y": round(self.curve_points[idx][1], 6),
                    "z": round(self.curve_points[idx][2], 6) if len(self.curve_points[idx]) > 2 else 0.0
                }
            }
            export_data["division_points"].append(point_data)
        
        # 添加统计信息
        export_data["statistics"] = {
            "parameter_range": {
                "min": round(min(division_t), 6),
                "max": round(max(division_t), 6)
            },
            "index_range": {
                "min": min(division_indices),
                "max": max(division_indices)
            },
            "total_curve_points": len(self.curve_points)
        }
        
        # Set output file path
        if output_file is None:
            # Get script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Set division_points.json to be saved in curve_json folder
            output_file = os.path.join(script_dir, 'curve_json', 'division_points.json')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Export to JSON file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"Division point data exported to: {output_file}")
        except Exception as e:
            print(f"Export failed: {e}")
            return None
        
        return export_data

def main():
    """
    Main function providing command line interface
    """
    import argparse
    import os
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Default JSON file path (using absolute path)
    DEFAULT_JSON_FILE = os.path.join(script_dir, "curve_json/curve_points_example.json")
    
    parser = argparse.ArgumentParser(description='Curve Distortion Analysis Tool')
    parser.add_argument('--json', type=str, help='JSON file path containing curve points, curvature centers and viewpoint position')
    parser.add_argument('--import-results', type=str, help='Import previously generated analysis results file path')
    parser.add_argument('--no-visualize', action='store_true', help='Do not display visualization results')
    parser.add_argument('--export', action='store_true', help='Export analysis results')
    parser.add_argument('--export-divisions', action='store_true', help='Export division point data to JSON file')
    
    args = parser.parse_args()
    
    # Create analyzer instance
    # Priority: command line arguments > default JSON file > no JSON file
    json_file_path = None
    if args.json:
        json_file_path = args.json
    elif os.path.exists(DEFAULT_JSON_FILE):
        print(f"Using default JSON file: {DEFAULT_JSON_FILE}")
        json_file_path = DEFAULT_JSON_FILE
    
    if json_file_path:
        analyzer = CurveDistortionAnalyzer(json_file_path)
    else:
        analyzer = CurveDistortionAnalyzer()
    
    # Import previous analysis results
    if args.import_results:
        print(f"Attempting to import analysis results file: {args.import_results}")
        if analyzer.import_results(args.import_results):
            # Visualization can be performed directly after successful import
            if not args.no_visualize:
                analyzer.visualize_results()
            print("Import and visualization completed")
            return
        else:
            print("Import failed, continuing with other operations")
    
    # If no JSON file is specified, prompt the user
    if not json_file_path:
        print("\nWarning: JSON file not found!")
        print("Please use the --json command line parameter to specify your JSON file path")
        print("Example: python curve_distortion_analysis.py --json your_filename.json")
        return
    
    # Execute analysis
    if analyzer.analyze():
        # Visualize results
        if not args.no_visualize:
            analyzer.visualize_results()
            # Add division point analysis visualization
            analyzer.visualize_division_points()
        
        # Export results
        if args.export:
            analyzer.export_results()
        
        # Export division point data (now executed by default, regardless of parameter)
        analyzer.export_division_points()
    
    print("Analysis completed")

if __name__ == "__main__":
    main()
    