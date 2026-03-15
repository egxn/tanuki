# Geometry Nodes Lister for Blender

This project contains scripts to list all geometry nodes available in Blender using **only** `bpy` and `json` as dependencies.

## ✨ Features

- 🔍 **Advanced search** by keyword
- 📊 **Automatic categorization** of nodes
- 📁 **JSON export** with complete metadata
- 🎯 **Only basic dependencies**: bpy and json
- 📱 **Clean interface** with emojis and formatting

## 📁 Files

- `tanuki.py` - **Main script** optimized with categorization and search
- `geometry_nodes_lister.py` - **Complete script** with detailed analysis and JSON export

## 🚀 How to use

### Method 1: From command line
```bash
blender --python tanuki.py
```

### Method 2: From Blender editor
1. Open Blender
2. Go to "Scripting" workspace
3. Open the file `tanuki.py` or `geometry_nodes_lister.py`
4. Click "Run Script"

### Method 3: From Python console in Blender
```python
exec(open('/path/to/tanuki.py').read())
```

## 📊 Node categories

The scripts automatically organize nodes into:

- **Input** - Input nodes (Cube, Cylinder, UV Sphere, etc.)
- **Output** - Output nodes (Group Output, Viewer)
- **Mesh** - Mesh operations (Boolean, Extrude, Subdivide, etc.)
- **Curve** - Curve operations (Resample, Fillet, Trim, etc.)
- **Volume** - Volume operations
- **Instances** - Instancing (Instance on Points, Realize Instances, etc.)
- **Attribute** - Attributes (Capture, Store, Statistics, etc.)
- **Utilities** - Utilities (Math, Mix, Switch, etc.)
- **Vector** - Vector operations
- **Material** - Materials
- **Transform** - Transformations
- **Math** - Mathematics
- **Color** - Colors
- **Other** - Others

## 🔍 Search functions

Both scripts include keyword search:

```python
# Search for nodes related to 'mesh'
results = search_nodes('mesh')

# Search for nodes related to 'curve'  
results = search_nodes('curve')
```

## 📤 JSON export

The `geometry_nodes_lister.py` script exports complete data to `/tmp/geometry_nodes_export.json`:

```json
{
  "geometry_nodes": [...],
  "categories": {...},
  "total_nodes": 150,
  "blender_version": "(3, 6, 0)",
  "export_timestamp": "3.6.0"
}
```

## 💡 Example output

```
============================================================
GEOMETRY NODES AVAILABLE IN BLENDER
============================================================
Blender Version: 3.6.0

Total Geometry Nodes found: 150+

=============== INPUT (25 nodes) ===============
  • Collection Info
    Type: GeometryNodeCollectionInfo
    Description: Get geometry from a collection

  • Cube
    Type: GeometryNodeMeshCube  
    Description: Generate a cube mesh

=============== MESH (35 nodes) ===============
  • Extrude Mesh
    Type: GeometryNodeExtrudeMesh
    Description: Extrude faces, edges or vertices

🔍 SEARCH DEMO
============================================================

🔍 'mesh' - 12 results:
  • Cube (Input)
  • Extrude Mesh (Mesh)
  • Mesh Boolean (Mesh)
  ... and 9 more
```

## ⚠️ Important notes

- Import errors for `bpy` in VS Code are **normal** - the module only exists inside Blender
- **Minimal dependencies**: Only uses `bpy` and `json` (Blender standard libraries)
- **No nodeitems_utils** or other external dependencies
- The script automatically detects Blender version and adjusts output

## 🔧 Dependencies

- ✅ `bpy` - Blender Python API (included with Blender)
- ✅ `json` - Python standard library
- ❌ ~~nodeitems_utils~~ - **Removed**
- ❌ ~~bl_operators~~ - **Removed**