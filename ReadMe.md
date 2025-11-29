# BLTopo: 曲线畸变分析与顶点处理工具

## 项目概述

BLTopo是一个集成了曲线畸变分析、顶点坐标处理和图像变换功能的工具集，主要用于分析3D曲线在不同视角下的畸变情况，处理顶点坐标数据，并进行相应的图像变换操作。该项目包含多个功能模块，可用于研究曲线形态、划分点计算、四边形生成以及透视变换等应用场景。

## 主要功能

- **曲线畸变分析**：计算曲线上各点的α角、细分点数等参数，并生成可视化结果
- **顶点坐标处理**：读取顶点坐标，将其分为上下两部分，生成四边形数据
- **划分点计算**：根据点密度分布和累积分布函数，在曲线上计算均匀分布的划分点
- **图像标注与变换**：在渲染图像上标注四边形，并进行透视变换生成条带图像
- **数据可视化**：生成曲线2D可视化、划分点分布图、累积分布图等多种图像
- **数据导出导入**：支持JSON格式的数据导出和导入功能

## 文件结构

```
github/
├── Blender/             # Blender项目文件目录
│   ├── test.blend       # 测试用Blender项目文件
├── blender_script/      # Blender相关Python脚本
│   ├── capture.py       # 捕获顶点屏幕坐标并渲染图像
│   └── curve_subdivision.py  # 曲线细分处理和可视化
├── curve_json/          # JSON数据文件目录
│   ├── curve_points_example.json      # 曲线点数据示例
│   ├── curve_points_贝塞尔曲线.001.json # 具体曲线的点数据
│   ├── division_points.json           # 计算得到的划分点数据
│   ├── judge.json                     # 四边形数据文件
│   └── vertex_coordinates_divided.json # 划分后的顶点坐标
├── render_output/       # 渲染输出和图像标注目录
│   ├── annotated_image.png               # 标注后的图像
│   ├── quadrilaterals_annotated.png      # 四边形标注图像
│   ├── rendered_image.png                # 渲染生成的图像
│   ├── vertex_coordinates.txt            # 顶点坐标文本文件
│   └── vertex_divided_quadrilaterals.png # 顶点划分四边形图像
├── strip_transformed/   # 变换后的条带图像目录
│   ├── strip_all_transformed_quadrilaterals.png     # 所有四边形变换后图像
│   ├── strip_all_transformed_quadrilaterals_seamless.png # 无缝拼接变换图像
│   └── strip_quadrilateral_xx_transformed.png       # 单个四边形变换图像
├── test_results/        # 测试结果可视化目录
│   ├── alpha_vs_subdivision.png       # α角与细分点数关系图
│   ├── cumulative_distribution.png    # 累积分布图
│   ├── curve_2d_visualization.png     # 曲线2D可视化
│   ├── curve_division_points.png      # 曲线划分点图
│   └── point_density_distribution.png # 点密度分布图
├── curve_distortion_analysis.py  # 曲线畸变分析主程序
├── integrated_workflow.py        # 集成工作流脚本
├── process_json_data.py          # JSON数据处理和图像标注
└── vertex_processor.py           # 顶点处理和四边形生成程序
```

### 目录说明

- **Blender/**：存储Blender项目文件，用于3D建模和渲染
- **blender_script/**：Blender中使用的Python脚本，负责顶点捕获和曲线处理
- **curve_json/**：存储各种JSON格式的数据文件，包括曲线点、划分点、四边形等数据
- **render_output/**：存储渲染图像和标注后的图像文件
- **strip_transformed/**：存储透视变换生成的条带图像
- **test_results/**：存储曲线分析的可视化结果图像

### 主要文件说明

- **curve_distortion_analysis.py**：核心分析程序，实现曲线畸变分析、划分点计算等功能
- **vertex_processor.py**：处理顶点坐标，生成四边形数据
- **integrated_workflow.py**：集成工作流，按顺序执行多个处理步骤
- **process_json_data.py**：处理JSON数据，生成四边形并进行图像标注
- **capture.py**：在Blender中捕获顶点屏幕坐标并渲染图像
- **curve_subdivision.py**：曲线细分处理和可视化功能

## 主要功能模块

### 1. 曲线畸变分析模块 (curve_distortion_analysis.py)

这是项目的核心模块，主要实现曲线畸变分析和划分点计算功能。

**核心功能：**
- 加载曲线点、曲率中心和视点位置数据
- 计算曲线上各点的α角（与视线的夹角）
- 根据α角计算细分点数N，用于后续的网格划分
- 计算点密度分布和累积分布函数
- 在曲线上计算均匀分布的划分点
- 生成多种可视化结果，包括：
  - 曲线2D可视化
  - 点密度分布图
  - 累积分布图
  - 划分点可视化
- 导出分析结果和划分点数据到JSON文件

**关键算法：**
- 使用梯形法则进行数值积分计算累积分布函数
- 线性插值求解划分点的位置
- 基于α角的自适应细分策略

### 2. 顶点处理模块 (vertex_processor.py)

该模块负责读取顶点坐标数据，将其分为上下两部分，并生成四边形数据。

**核心功能：**
- 从文本文件读取顶点坐标数据
- 计算中点Y坐标，将顶点分为上下两部分
- 创建四边形数据，将上下对应的顶点连接
- 生成四边形的JSON数据格式
- 在渲染图像上绘制四边形

### 3. 集成工作流模块 (integrated_workflow.py)

该模块将多个处理步骤集成到一个工作流中，按顺序执行。

**核心功能：**
- 检查必要文件的存在性
- 从judge.json读取四边形数据
- 在渲染图像上标注四边形
- 从division_points.json读取划分点数据
- 执行透视变换，生成条带图像
- 创建无缝拼接的条带图像

### 4. JSON数据处理模块 (process_json_data.py)

该模块处理各种JSON数据文件，生成四边形并进行图像标注。

**核心功能：**
- 加载划分点和顶点坐标数据
- 生成四边形并存储到judge.json
- 在图像上标注四边形和顶点
- 支持不同数据格式的转换和处理

### 5. Blender相关功能模块

#### 5.1 顶点捕获模块 (capture.py)

在Blender中执行，捕获物体顶点的屏幕坐标并渲染图像。

**核心功能：**
- 列出场景中的物体和摄像机
- 设置渲染摄像机和输出路径
- 渲染图像并保存到指定目录
- 计算并保存顶点的屏幕坐标

#### 5.2 曲线细分处理模块 (curve_subdivision.py)

在Blender中执行，处理曲线细分并可视化。

**核心功能：**
- 收集曲线基本信息
- 支持Bezier和NURBS两种曲线类型
- 绘制曲线结构，支持以摄像机为原点的坐标系
- 在图像上标记摄像机位置和坐标
- 列出场景中所有可用的曲线对象

## 使用指南和示例

### 环境要求

- Python 3.7+
- 依赖包：numpy, matplotlib, PIL (Pillow), opencv-python
- Blender 3.0+（用于3D建模和顶点捕获）

### 安装依赖

```bash
pip install numpy matplotlib pillow opencv-python
```

### 基本工作流程

1. **准备阶段**：在Blender中设置3D模型和摄像机
2. **数据采集**：运行Blender脚本捕获顶点坐标并渲染图像
3. **数据分析**：执行曲线畸变分析，计算划分点
4. **四边形生成**：处理顶点坐标，生成四边形数据
5. **图像处理**：执行透视变换，生成条带图像

### 使用示例

#### 1. Blender顶点捕获

在Blender中打开test.blend文件，然后在脚本编辑器中打开并运行`blender_script/capture.py`。

**配置参数：**
在脚本中修改以下参数以适应您的场景：
```python
object_name = "wan.002"  # 要分析的物体名称
camera_name = "Camera.004"  # 使用的摄像机名称
```

#### 2. 曲线畸变分析

使用以下命令运行曲线畸变分析：

```bash
python curve_distortion_analysis.py --json curve_json/curve_points_example.json --export
```

**参数说明：**
- `--json`：指定包含曲线点数据的JSON文件路径
- `--export`：导出分析结果到JSON文件
- `--export-divisions`：导出划分点数据到JSON文件
- `--no-visualize`：不显示可视化结果
- `--import-results`：导入之前生成的分析结果文件

#### 3. 顶点处理和四边形生成

运行顶点处理程序：

```bash
python vertex_processor.py
```

程序会自动读取默认路径的顶点坐标文件，并生成四边形数据。

#### 4. 执行集成工作流

运行集成工作流脚本来执行完整的处理流程：

```bash
python integrated_workflow.py
```

该脚本会自动检查必要文件，读取四边形数据，执行透视变换，并生成条带图像。

### 常见问题解答

**Q1: 找不到曲线点数据文件怎么办？**
A: 请确保您已经在Blender中运行了相关脚本来生成曲线点数据，或者使用`--json`参数指定正确的JSON文件路径。

**Q2: 透视变换生成的条带图像质量不佳怎么办？**
A: 可以尝试调整曲线畸变分析中的参数，增加细分点数，或者优化Blender中的摄像机位置和视角。

**Q3: 如何查看场景中的可用曲线对象？**
A: 在Blender脚本中调用`list_available_curves()`函数，或者在Blender界面中查看曲线对象名称。

## 输出文件说明

### 分析结果

- **test_results/curve_2d_visualization.png**：曲线的2D可视化图像
- **test_results/point_density_distribution.png**：点密度分布图
- **test_results/cumulative_distribution.png**：累积分布图
- **test_results/curve_division_points.png**：曲线划分点可视化

### 处理结果

- **curve_json/judge.json**：生成的四边形数据
- **curve_json/division_points.json**：计算的划分点数据
- **strip_transformed/strip_quadrilateral_xx_transformed.png**：变换后的条带图像
- **strip_transformed/strip_all_transformed_quadrilaterals.png**：所有四边形的变换结果

## 注意事项

1. 确保文件路径设置正确，特别是在不同操作系统间切换时
2. 在运行集成工作流前，确保所有前置文件都已正确生成
3. 对于大型模型，可能需要调整参数以获得更好的性能和结果
4. Blender脚本需要在Blender环境中运行，而不是直接在Python环境中

# BLTopo: Curve Distortion Analysis and Vertex Processing Tool

## Project Overview

BLTopo is a comprehensive toolkit that integrates curve distortion analysis, vertex coordinate processing, and image transformation capabilities. It is primarily designed to analyze distortion of 3D curves from different viewing angles, process vertex coordinate data, and perform corresponding image transformation operations. The project includes multiple functional modules that can be used for curve morphology research, division point calculation, quadrilateral generation, and perspective transformation applications.

## Main Features

- **Curve Distortion Analysis**: Calculate parameters such as α angles and subdivision points for each point on the curve, and generate visualization results
- **Vertex Coordinate Processing**: Read vertex coordinates, divide them into upper and lower parts, and generate quadrilateral data
- **Division Point Calculation**: Calculate evenly distributed division points on curves based on point density distribution and cumulative distribution functions
- **Image Annotation and Transformation**: Annotate quadrilaterals on rendered images and perform perspective transformation to generate strip images
- **Data Visualization**: Generate multiple visualizations including 2D curve visualization, division point distribution charts, and cumulative distribution charts
- **Data Import/Export**: Support data import and export in JSON format

## File Structure

```
github/
├── Blender/             # Blender project files directory
│   ├── test.blend       # Test Blender project file
├── blender_script/      # Blender-related Python scripts
│   ├── capture.py       # Capture vertex screen coordinates and render images
│   └── curve_subdivision.py  # Curve subdivision processing and visualization
├── curve_json/          # JSON data files directory
│   ├── curve_points_example.json      # Curve point data example
│   ├── curve_points_贝塞尔曲线.001.json # Specific curve point data
│   ├── division_points.json           # Calculated division points data
│   ├── judge.json                     # Quadrilateral data file
│   └── vertex_coordinates_divided.json # Divided vertex coordinates
├── render_output/       # Render output and image annotation directory
│   ├── annotated_image.png               # Annotated image
│   ├── quadrilaterals_annotated.png      # Quadrilateral annotated image
│   ├── rendered_image.png                # Rendered image
│   ├── vertex_coordinates.txt            # Vertex coordinates text file
│   └── vertex_divided_quadrilaterals.png # Vertex divided quadrilaterals image
├── strip_transformed/   # Transformed strip images directory
│   ├── strip_all_transformed_quadrilaterals.png     # All transformed quadrilaterals image
│   ├── strip_all_transformed_quadrilaterals_seamless.png # Seamlessly stitched transformed image
│   └── strip_quadrilateral_xx_transformed.png       # Individual quadrilateral transformed images
├── test_results/        # Test results visualization directory
│   ├── alpha_vs_subdivision.png       # Relationship between α angle and subdivision points
│   ├── cumulative_distribution.png    # Cumulative distribution chart
│   ├── curve_2d_visualization.png     # 2D curve visualization
│   ├── curve_division_points.png      # Curve division points chart
│   └── point_density_distribution.png # Point density distribution chart
├── curve_distortion_analysis.py  # Main curve distortion analysis program
├── integrated_workflow.py        # Integrated workflow script
├── process_json_data.py          # JSON data processing and image annotation
└── vertex_processor.py           # Vertex processing and quadrilateral generation program
```

### Directory Description

- **Blender/**: Stores Blender project files for 3D modeling and rendering
- **blender_script/**: Python scripts used in Blender for vertex capture and curve processing
- **curve_json/**: Stores various JSON format data files including curve points, division points, and quadrilateral data
- **render_output/**: Stores rendered images and annotated image files
- **strip_transformed/**: Stores strip images generated through perspective transformation
- **test_results/**: Stores visualization results of curve analysis

### Main File Description

- **curve_distortion_analysis.py**: Core analysis program implementing curve distortion analysis and division point calculation
- **vertex_processor.py**: Processes vertex coordinates and generates quadrilateral data
- **integrated_workflow.py**: Integrates multiple processing steps into a workflow for sequential execution
- **process_json_data.py**: Processes JSON data, generates quadrilaterals, and performs image annotation
- **capture.py**: Captures screen coordinates of vertices and renders images in Blender
- **curve_subdivision.py**: Curve subdivision processing and visualization functionality

## Main Function Modules

### 1. Curve Distortion Analysis Module (curve_distortion_analysis.py)

This is the core module of the project, primarily implementing curve distortion analysis and division point calculation functionality.

**Core Functions:**
- Load curve points, curvature centers, and viewpoint position data
- Calculate α angles (angles with the line of sight) for each point on the curve
- Calculate subdivision points N based on α angles for subsequent mesh division
- Calculate point density distribution and cumulative distribution function
- Calculate evenly distributed division points on the curve
- Generate multiple visualizations, including:
  - 2D curve visualization
  - Point density distribution chart
  - Cumulative distribution chart
  - Division point visualization
- Export analysis results and division points data to JSON files

**Key Algorithms:**
- Numerical integration using the trapezoidal rule to calculate the cumulative distribution function
- Linear interpolation to solve for division point positions
- Adaptive subdivision strategy based on α angles

### 2. Vertex Processing Module (vertex_processor.py)

This module is responsible for reading vertex coordinate data, dividing it into upper and lower parts, and generating quadrilateral data.

**Core Functions:**
- Read vertex coordinate data from text files
- Calculate midpoint Y-coordinate to divide vertices into upper and lower parts
- Create quadrilateral data by connecting corresponding upper and lower vertices
- Generate JSON data format for quadrilaterals
- Draw quadrilaterals on rendered images

### 3. Integrated Workflow Module (integrated_workflow.py)

This module integrates multiple processing steps into a workflow and executes them sequentially.

**Core Functions:**
- Check existence of necessary files
- Read quadrilateral data from judge.json
- Annotate quadrilaterals on rendered images
- Read division points data from division_points.json
- Execute perspective transformation to generate strip images
- Create seamlessly stitched strip images

### 4. JSON Data Processing Module (process_json_data.py)

This module processes various JSON data files, generates quadrilaterals, and performs image annotation.

**Core Functions:**
- Load division points and vertex coordinate data
- Generate quadrilaterals and store them in judge.json
- Annotate quadrilaterals and vertices on images
- Support conversion and processing of different data formats

### 5. Blender-related Function Modules

#### 5.1 Vertex Capture Module (capture.py)

Executed in Blender to capture screen coordinates of object vertices and render images.

**Core Functions:**
- List objects and cameras in the scene
- Set rendering camera and output path
- Render images and save to specified directory
- Calculate and save screen coordinates of vertices

#### 5.2 Curve Subdivision Processing Module (curve_subdivision.py)

Executed in Blender to process curve subdivision and visualization.

**Core Functions:**
- Collect basic curve information
- Support both Bezier and NURBS curve types
- Draw curve structure, supporting camera-originated coordinate system
- Mark camera position and coordinates on images
- List all available curve objects in the scene

## Usage Guide and Examples

### Environment Requirements

- Python 3.7+
- Dependencies: numpy, matplotlib, PIL (Pillow), opencv-python
- Blender 3.0+ (for 3D modeling and vertex capture)

### Installing Dependencies

```bash
pip install numpy matplotlib pillow opencv-python
```

### Basic Workflow

1. **Preparation Phase**: Set up 3D models and cameras in Blender
2. **Data Acquisition**: Run Blender scripts to capture vertex coordinates and render images
3. **Data Analysis**: Perform curve distortion analysis to calculate division points
4. **Quadrilateral Generation**: Process vertex coordinates to generate quadrilateral data
5. **Image Processing**: Execute perspective transformation to generate strip images

### Usage Examples

#### 1. Blender Vertex Capture

Open the test.blend file in Blender, then open and run `blender_script/capture.py` in the script editor.

**Configuration Parameters:**
Modify the following parameters in the script to suit your scene:
```python
object_name = "wan.002"  # Name of the object to analyze
camera_name = "Camera.004"  # Name of the camera to use
```

#### 2. Curve Distortion Analysis

Run the curve distortion analysis with the following command:

```bash
python curve_distortion_analysis.py --json curve_json/curve_points_example.json --export
```

**Parameter Description:**
- `--json`: Specify the path to the JSON file containing curve point data
- `--export`: Export analysis results to JSON file
- `--export-divisions`: Export division points data to JSON file
- `--no-visualize`: Do not display visualization results
- `--import-results`: Import previously generated analysis results file

#### 3. Vertex Processing and Quadrilateral Generation

Run the vertex processing program:

```bash
python vertex_processor.py
```

The program will automatically read the vertex coordinate file from the default path and generate quadrilateral data.

#### 4. Execute Integrated Workflow

Run the integrated workflow script to execute the complete processing flow:

```bash
python integrated_workflow.py
```

This script will automatically check necessary files, read quadrilateral data, execute perspective transformation, and generate strip images.

### Frequently Asked Questions

**Q1: What if I can't find the curve point data file?**
A: Make sure you have run the relevant scripts in Blender to generate curve point data, or use the `--json` parameter to specify the correct JSON file path.

**Q2: What if the quality of the strip images generated through perspective transformation is poor?**
A: You can try adjusting parameters in the curve distortion analysis, increasing the number of subdivision points, or optimizing camera position and viewing angle in Blender.

**Q3: How to view available curve objects in the scene?**
A: Call the `list_available_curves()` function in the Blender script, or view curve object names in the Blender interface.

## Output File Description

### Analysis Results

- **test_results/curve_2d_visualization.png**: 2D visualization image of the curve
- **test_results/point_density_distribution.png**: Point density distribution chart
- **test_results/cumulative_distribution.png**: Cumulative distribution chart
- **test_results/curve_division_points.png**: Curve division point visualization

### Processing Results

- **curve_json/judge.json**: Generated quadrilateral data
- **curve_json/division_points.json**: Calculated division points data
- **strip_transformed/strip_quadrilateral_xx_transformed.png**: Transformed strip images
- **strip_transformed/strip_all_transformed_quadrilaterals.png**: Transformation results of all quadrilaterals

## Notes

1. Ensure file paths are set correctly, especially when switching between different operating systems
2. Make sure all prerequisite files are generated correctly before running the integrated workflow
3. For large models, parameters may need to be adjusted for better performance and results
4. Blender scripts need to be run in the Blender environment, not directly in the Python environment