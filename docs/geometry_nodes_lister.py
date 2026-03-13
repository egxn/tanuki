#!/usr/bin/env python3
"""
Script to list all possible Geometry Nodes in Blender using bpy
Requires execution inside Blender or with bpy installed
Only uses bpy and json as dependencies
"""

import bpy
import json


def analyze_node_sockets(node_class):
    """Analyzes the inputs and outputs of a geometry node"""
    inputs = []
    outputs = []
    
    try:
        if hasattr(node_class, 'bl_rna'):
            bl_rna = node_class.bl_rna
            
            # Method 1: Extract from bl_rna properties
            if hasattr(bl_rna, 'properties'):
                for prop in bl_rna.properties:
                    prop_name = prop.identifier.lower()
                    prop_type = getattr(prop, 'type', 'UNKNOWN')
                    
                    # Enhanced socket detection patterns
                    input_patterns = ['input', 'socket_in', 'factor', 'value', 'geometry', 'mesh', 'curve', 
                                    'points', 'volume', 'instances', 'material', 'vector', 'color', 
                                    'strength', 'radius', 'count', 'seed', 'scale', 'offset']
                    
                    output_patterns = ['output', 'socket_out', 'result', 'geometry_out']
                    
                    # Check for input patterns
                    if any(pattern in prop_name for pattern in input_patterns):
                        # Skip internal blender properties
                        if not prop_name.startswith(('bl_', 'rna_')):
                            socket_info = {
                                'name': prop.name,
                                'identifier': prop.identifier,
                                'type': prop_type,
                                'description': getattr(prop, 'description', 'N/A'),
                                'subtype': getattr(prop, 'subtype', 'NONE') if hasattr(prop, 'subtype') else 'NONE'
                            }
                            
                            # Add range information for numeric types
                            if prop_type in ['FLOAT', 'INT']:
                                socket_info['min'] = getattr(prop, 'soft_min', getattr(prop, 'hard_min', None))
                                socket_info['max'] = getattr(prop, 'soft_max', getattr(prop, 'hard_max', None))
                                socket_info['default'] = getattr(prop, 'default', None)
                            
                            # Add enum options
                            elif prop_type == 'ENUM':
                                if hasattr(prop, 'enum_items'):
                                    socket_info['options'] = [item.identifier for item in prop.enum_items]
                                    socket_info['default'] = getattr(prop, 'default', None)
                            
                            inputs.append(socket_info)
                    
                    # Check for output patterns
                    elif any(pattern in prop_name for pattern in output_patterns):
                        if not prop_name.startswith(('bl_', 'rna_')):
                            outputs.append({
                                'name': prop.name,
                                'identifier': prop.identifier,
                                'type': prop_type,
                                'description': getattr(prop, 'description', 'N/A'),
                                'subtype': getattr(prop, 'subtype', 'NONE') if hasattr(prop, 'subtype') else 'NONE'
                            })
            
            # Method 2: Check class annotations
            if hasattr(node_class, '__annotations__'):
                annotations = node_class.__annotations__
                for name, annotation in annotations.items():
                    if 'input' in name.lower():
                        inputs.append({
                            'name': name,
                            'identifier': name,
                            'type': str(annotation),
                            'description': 'Socket input detected from annotations',
                            'source': 'annotation'
                        })
                    elif 'output' in name.lower():
                        outputs.append({
                            'name': name,
                            'identifier': name,
                            'type': str(annotation),
                            'description': 'Socket output detected from annotations',
                            'source': 'annotation'
                        })
    
    except Exception as e:
        node_type = node_class.__name__
        
        if 'Input' in node_type:
            outputs.append({
                'name': 'Geometry/Value',
                'identifier': 'output',
                'type': 'GEOMETRY',
                'description': 'Main output of input node'
            })
        elif 'Output' in node_type:
            inputs.append({
                'name': 'Geometry',
                'identifier': 'geometry',
                'type': 'GEOMETRY', 
                'description': 'Geometry input'
            })
        else:
            inputs.append({
                'name': 'Geometry',
                'identifier': 'geometry',
                'type': 'GEOMETRY',
                'description': 'Geometry input (inferred)'
            })
            outputs.append({
                'name': 'Geometry',
                'identifier': 'geometry',
                'type': 'GEOMETRY',
                'description': 'Geometry output (inferred)'
            })
    
    return inputs, outputs


def analyze_geometry_node_sockets_enhanced(node_class):
    """Enhanced socket analysis specifically for geometry nodes"""
    inputs = []
    outputs = []
    node_type = node_class.__name__
    
    # Comprehensive geometry node socket mapping based on Blender documentation
    socket_definitions = {
        # Input Nodes
        'GeometryNodeCollectionInfo': {
            'inputs': [
                {'name': 'Collection', 'type': 'COLLECTION', 'description': 'Collection to get geometry from'},
                {'name': 'Separate Children', 'type': 'BOOLEAN', 'description': 'Output each child as a separate instance'},
                {'name': 'Reset Children', 'type': 'BOOLEAN', 'description': 'Reset the transforms of children'}
            ],
            'outputs': [
                {'name': 'Geometry', 'type': 'GEOMETRY', 'description': 'Geometry from the collection'}
            ]
        },
        'GeometryNodeObjectInfo': {
            'inputs': [
                {'name': 'Object', 'type': 'OBJECT', 'description': 'Object to get info from'},
                {'name': 'As Instance', 'type': 'BOOLEAN', 'description': 'Output object as instance'}
            ],
            'outputs': [
                {'name': 'Location', 'type': 'VECTOR', 'description': 'Location of the object'},
                {'name': 'Rotation', 'type': 'VECTOR', 'description': 'Rotation of the object'},
                {'name': 'Scale', 'type': 'VECTOR', 'description': 'Scale of the object'},
                {'name': 'Geometry', 'type': 'GEOMETRY', 'description': 'Geometry of the object'}
            ]
        },
        
        # Mesh Nodes
        'GeometryNodeMeshBoolean': {
            'inputs': [
                {'name': 'Mesh 1', 'type': 'GEOMETRY', 'description': 'First mesh input'},
                {'name': 'Mesh 2', 'type': 'GEOMETRY', 'description': 'Second mesh input'},
                {'name': 'Self Intersection', 'type': 'BOOLEAN', 'description': 'Allow self intersection'},
                {'name': 'Hole Tolerant', 'type': 'BOOLEAN', 'description': 'Hole tolerant processing'}
            ],
            'outputs': [
                {'name': 'Mesh', 'type': 'GEOMETRY', 'description': 'Result of boolean operation'},
                {'name': 'Intersecting Edges', 'type': 'BOOLEAN', 'description': 'Edges that intersect'}
            ]
        },
        'GeometryNodeExtrudeMesh': {
            'inputs': [
                {'name': 'Mesh', 'type': 'GEOMETRY', 'description': 'Input mesh'},
                {'name': 'Selection', 'type': 'BOOLEAN', 'description': 'Selection of faces to extrude'},
                {'name': 'Offset', 'type': 'VECTOR', 'description': 'Offset vector for extrusion'},
                {'name': 'Offset Scale', 'type': 'FLOAT', 'description': 'Scale for offset'},
                {'name': 'Individual', 'type': 'BOOLEAN', 'description': 'Extrude faces individually'}
            ],
            'outputs': [
                {'name': 'Mesh', 'type': 'GEOMETRY', 'description': 'Extruded mesh'},
                {'name': 'Top', 'type': 'BOOLEAN', 'description': 'Top faces selection'},
                {'name': 'Side', 'type': 'BOOLEAN', 'description': 'Side faces selection'}
            ]
        },
        
        # Curve Nodes
        'GeometryNodeCurveToMesh': {
            'inputs': [
                {'name': 'Curve', 'type': 'GEOMETRY', 'description': 'Input curve'},
                {'name': 'Profile Curve', 'type': 'GEOMETRY', 'description': 'Profile curve for sweep'},
                {'name': 'Fill Caps', 'type': 'BOOLEAN', 'description': 'Fill end caps'}
            ],
            'outputs': [
                {'name': 'Mesh', 'type': 'GEOMETRY', 'description': 'Generated mesh'}
            ]
        },
        'GeometryNodeResampleCurve': {
            'inputs': [
                {'name': 'Curve', 'type': 'GEOMETRY', 'description': 'Input curve'},
                {'name': 'Selection', 'type': 'BOOLEAN', 'description': 'Curve selection'},
                {'name': 'Count', 'type': 'INT', 'description': 'Number of sample points'},
                {'name': 'Length', 'type': 'FLOAT', 'description': 'Length between points'}
            ],
            'outputs': [
                {'name': 'Curve', 'type': 'GEOMETRY', 'description': 'Resampled curve'}
            ]
        },
        
        # Instance Nodes
        'GeometryNodeInstanceOnPoints': {
            'inputs': [
                {'name': 'Points', 'type': 'GEOMETRY', 'description': 'Points to instance on'},
                {'name': 'Selection', 'type': 'BOOLEAN', 'description': 'Point selection'},
                {'name': 'Instance', 'type': 'GEOMETRY', 'description': 'Geometry to instance'},
                {'name': 'Pick Instance', 'type': 'BOOLEAN', 'description': 'Pick random instances'},
                {'name': 'Instance Index', 'type': 'INT', 'description': 'Instance index'},
                {'name': 'Rotation', 'type': 'VECTOR', 'description': 'Rotation for instances'},
                {'name': 'Scale', 'type': 'VECTOR', 'description': 'Scale for instances'}
            ],
            'outputs': [
                {'name': 'Instances', 'type': 'GEOMETRY', 'description': 'Generated instances'}
            ]
        },
        
        # Attribute Nodes
        'GeometryNodeCaptureAttribute': {
            'inputs': [
                {'name': 'Geometry', 'type': 'GEOMETRY', 'description': 'Input geometry'},
                {'name': 'Value', 'type': 'FLOAT', 'description': 'Value to capture'},
                {'name': 'Vector', 'type': 'VECTOR', 'description': 'Vector to capture'},
                {'name': 'Color', 'type': 'RGBA', 'description': 'Color to capture'},
                {'name': 'Boolean', 'type': 'BOOLEAN', 'description': 'Boolean to capture'},
                {'name': 'Integer', 'type': 'INT', 'description': 'Integer to capture'}
            ],
            'outputs': [
                {'name': 'Geometry', 'type': 'GEOMETRY', 'description': 'Output geometry'},
                {'name': 'Attribute', 'type': 'FLOAT', 'description': 'Captured attribute'}
            ]
        },
        
        # Primitive Nodes
        'GeometryNodeMeshCube': {
            'inputs': [
                {'name': 'Size', 'type': 'VECTOR', 'description': 'Size of the cube'},
                {'name': 'Vertices X', 'type': 'INT', 'description': 'Vertices along X axis'},
                {'name': 'Vertices Y', 'type': 'INT', 'description': 'Vertices along Y axis'},
                {'name': 'Vertices Z', 'type': 'INT', 'description': 'Vertices along Z axis'}
            ],
            'outputs': [
                {'name': 'Mesh', 'type': 'GEOMETRY', 'description': 'Generated cube mesh'},
                {'name': 'UV Map', 'type': 'VECTOR', 'description': 'UV coordinates'}
            ]
        },
        'GeometryNodeMeshCylinder': {
            'inputs': [
                {'name': 'Vertices', 'type': 'INT', 'description': 'Number of vertices'},
                {'name': 'Side Segments', 'type': 'INT', 'description': 'Side segments'},
                {'name': 'Fill Segments', 'type': 'INT', 'description': 'Fill segments'},
                {'name': 'Radius Top', 'type': 'FLOAT', 'description': 'Top radius'},
                {'name': 'Radius Bottom', 'type': 'FLOAT', 'description': 'Bottom radius'},
                {'name': 'Depth', 'type': 'FLOAT', 'description': 'Cylinder depth'}
            ],
            'outputs': [
                {'name': 'Mesh', 'type': 'GEOMETRY', 'description': 'Generated cylinder mesh'},
                {'name': 'Top', 'type': 'BOOLEAN', 'description': 'Top faces selection'},
                {'name': 'Bottom', 'type': 'BOOLEAN', 'description': 'Bottom faces selection'},
                {'name': 'Side', 'type': 'BOOLEAN', 'description': 'Side faces selection'},
                {'name': 'UV Map', 'type': 'VECTOR', 'description': 'UV coordinates'}
            ]
        }
    }
    
    # Try to find exact match
    if node_type in socket_definitions:
        definition = socket_definitions[node_type]
        
        # Add inputs
        for i, input_def in enumerate(definition.get('inputs', [])):
            inputs.append({
                'name': input_def['name'],
                'identifier': input_def['name'].lower().replace(' ', '_'),
                'type': input_def['type'],
                'description': input_def['description'],
                'socket_index': i,
                'source': 'known_definition'
            })
        
        # Add outputs
        for i, output_def in enumerate(definition.get('outputs', [])):
            outputs.append({
                'name': output_def['name'],
                'identifier': output_def['name'].lower().replace(' ', '_'),
                'type': output_def['type'],
                'description': output_def['description'],
                'socket_index': i,
                'source': 'known_definition'
            })
    
    # Fallback to pattern matching for unknown nodes
    else:
        socket_patterns = {
            'Mesh': {
                'inputs': ['Mesh', 'Selection'],
                'outputs': ['Mesh']
            },
            'Curve': {
                'inputs': ['Curve', 'Selection'],
                'outputs': ['Curve']
            },
            'Volume': {
                'inputs': ['Volume', 'Density'],
                'outputs': ['Volume']
            },
            'Instance': {
                'inputs': ['Points', 'Instance', 'Selection'],
                'outputs': ['Instances']
            },
            'Attribute': {
                'inputs': ['Geometry', 'Selection', 'Value'],
                'outputs': ['Geometry']
            },
            'Input': {
                'inputs': [],
                'outputs': ['Value']
            },
            'Output': {
                'inputs': ['Geometry'],
                'outputs': []
            }
        }
        
        # Pattern matching
        for pattern, sockets in socket_patterns.items():
            if pattern in node_type:
                # Add predicted inputs
                for i, input_name in enumerate(sockets['inputs']):
                    inputs.append({
                        'name': input_name,
                        'identifier': input_name.lower(),
                        'type': 'GEOMETRY' if input_name in ['Geometry', 'Mesh', 'Curve', 'Volume'] else 'VALUE',
                        'description': f'{input_name} input socket (predicted)',
                        'socket_index': i,
                        'source': 'pattern_matching'
                    })
                
                # Add predicted outputs
                for i, output_name in enumerate(sockets['outputs']):
                    outputs.append({
                        'name': output_name,
                        'identifier': output_name.lower(),
                        'type': 'GEOMETRY' if output_name in ['Geometry', 'Mesh', 'Curve', 'Volume'] else 'VALUE',
                        'description': f'{output_name} output socket (predicted)',
                        'socket_index': i,
                        'source': 'pattern_matching'
                    })
                break
    
    return inputs, outputs


def get_geometry_node_categories():
    """Gets logical categories based on geometry node types"""
    node_types = get_all_geometry_node_types()
    
    categories = {}
    for node in node_types:
        category = categorize_node(node['type'])
        if category not in categories:
            categories[category] = []
        categories[category].append(node)
    
    return categories


def categorize_node(node_type):
    """Categorizes a node based on its type"""
    if 'Input' in node_type:
        return 'Input'
    elif 'Output' in node_type:
        return 'Output'
    elif 'Mesh' in node_type:
        return 'Mesh'
    elif 'Curve' in node_type:
        return 'Curve'
    elif 'Volume' in node_type:
        return 'Volume'
    elif 'Instance' in node_type:
        return 'Instances'
    elif 'Attribute' in node_type:
        return 'Attribute'
    elif 'Utilities' in node_type or 'Utility' in node_type:
        return 'Utilities'
    elif 'Vector' in node_type:
        return 'Vector'
    elif 'Material' in node_type:
        return 'Material'
    elif 'Texture' in node_type:
        return 'Texture'
    elif 'Transform' in node_type:
        return 'Transform'
    elif 'Math' in node_type:
        return 'Math'
    elif 'Color' in node_type:
        return 'Color'
    else:
        return 'Other'


def get_node_properties(node_class):
    """Gets detailed properties of a node"""
    properties = []
    functions = []
    
    try:
        if hasattr(node_class, 'bl_rna'):
            bl_rna = node_class.bl_rna
            
            if hasattr(bl_rna, 'properties'):
                for prop in bl_rna.properties:
                    if not prop.identifier.startswith('bl_') and not prop.identifier.startswith('rna_'):
                        prop_info = {
                            'name': prop.name,
                            'identifier': prop.identifier,
                            'type': prop.type,
                            'description': getattr(prop, 'description', 'N/A'),
                            'default': getattr(prop, 'default', 'N/A'),
                            'is_readonly': getattr(prop, 'is_readonly', False)
                        }
                        
                        if prop.type == 'ENUM':
                            if hasattr(prop, 'enum_items'):
                                prop_info['enum_items'] = [item.identifier for item in prop.enum_items]
                        elif prop.type in ['FLOAT', 'INT']:
                            prop_info['min'] = getattr(prop, 'hard_min', 'N/A')
                            prop_info['max'] = getattr(prop, 'hard_max', 'N/A')
                        
                        properties.append(prop_info)
            
            if hasattr(bl_rna, 'functions'):
                for func in bl_rna.functions:
                    func_info = {
                        'name': func.identifier,
                        'description': getattr(func, 'description', 'N/A'),
                        'parameters': []
                    }
                    
                    if hasattr(func, 'parameters'):
                        for param in func.parameters:
                            param_info = {
                                'name': param.identifier,
                                'type': param.type,
                                'description': getattr(param, 'description', 'N/A')
                            }
                            func_info['parameters'].append(param_info)
                    
                    functions.append(func_info)
                    
    except Exception as e:
        pass
    
    return properties, functions


def categorize_nodes(node_types):
    """Categorizes geometry nodes into logical groups"""
    categories = {}
    
    for node in node_types:
        node_type = node['type']
        
        if 'Input' in node_type:
            category = 'Input'
        elif 'Output' in node_type:
            category = 'Output'
        elif 'Mesh' in node_type:
            category = 'Mesh'
        elif 'Curve' in node_type:
            category = 'Curve'
        elif 'Volume' in node_type:
            category = 'Volume'
        elif 'Instances' in node_type or 'Instance' in node_type:
            category = 'Instances'
        elif 'Attribute' in node_type:
            category = 'Attribute'
        elif 'Utilities' in node_type or 'Utility' in node_type:
            category = 'Utilities'
        elif 'Vector' in node_type:
            category = 'Vector'
        elif 'Material' in node_type:
            category = 'Material'
        elif 'Texture' in node_type:
            category = 'Texture'
        elif 'Transform' in node_type:
            category = 'Transform'
        elif 'Points' in node_type:
            category = 'Points'
        elif 'Collection' in node_type:
            category = 'Collection'
        elif 'Object' in node_type:
            category = 'Object'
        elif 'String' in node_type or 'Text' in node_type:
            category = 'Text'
        elif 'Math' in node_type or 'Boolean' in node_type:
            category = 'Math'
        elif 'Repeat' in node_type or 'Loop' in node_type:
            category = 'Control Flow'
        else:
            category = 'Other'
        
        if category not in categories:
            categories[category] = []
        categories[category].append(node)
    
    return categories


def get_all_geometry_node_types():
    """Gets all geometry node types available with detailed information"""
    node_types = []
    
    for node_type in dir(bpy.types):
        if node_type.startswith('GeometryNode'):
            try:
                node_class = getattr(bpy.types, node_type)
                if hasattr(node_class, 'bl_rna'):
                    node_info = {
                        'type': node_type,
                        'name': node_class.bl_rna.name if hasattr(node_class.bl_rna, 'name') else 'N/A',
                        'description': node_class.bl_rna.description if hasattr(node_class.bl_rna, 'description') else 'N/A'
                    }
                    
                    # Analyze sockets using multiple methods
                    inputs, outputs = analyze_node_sockets(node_class)
                    enhanced_inputs, enhanced_outputs = analyze_geometry_node_sockets_enhanced(node_class)
                    
                    # Combine results, prioritizing actual detected sockets
                    if not inputs and enhanced_inputs:
                        inputs = enhanced_inputs
                    elif inputs and enhanced_inputs:
                        # Merge unique sockets from both methods
                        existing_identifiers = {inp['identifier'] for inp in inputs}
                        for enhanced_inp in enhanced_inputs:
                            if enhanced_inp['identifier'] not in existing_identifiers:
                                inputs.append(enhanced_inp)
                    
                    if not outputs and enhanced_outputs:
                        outputs = enhanced_outputs
                    elif outputs and enhanced_outputs:
                        # Merge unique sockets from both methods
                        existing_identifiers = {out['identifier'] for out in outputs}
                        for enhanced_out in enhanced_outputs:
                            if enhanced_out['identifier'] not in existing_identifiers:
                                outputs.append(enhanced_out)
                    
                    node_info['inputs'] = inputs
                    node_info['outputs'] = outputs
                    node_info['socket_analysis_methods'] = ['property_scan', 'pattern_matching']
                    
                    properties, functions = get_node_properties(node_class)
                    node_info['properties'] = properties
                    node_info['functions'] = functions
                    
                    node_info['base_classes'] = [base.__name__ for base in node_class.__bases__ if hasattr(base, '__name__')]
                    node_info['module'] = getattr(node_class, '__module__', 'N/A')
                    
                    node_types.append(node_info)
            except Exception as e:
                pass
    
    return node_types


def print_geometry_nodes_summary():
    """Prints a summary of all geometry nodes with detailed information"""
    node_types = get_all_geometry_node_types()
    
    categories = {}
    for node in node_types:
        category = categorize_node(node['type'])
        if category not in categories:
            categories[category] = []
        categories[category].append(node)
    
    total_inputs = sum(len(node['inputs']) for node in node_types)
    total_outputs = sum(len(node['outputs']) for node in node_types)
    total_properties = sum(len(node['properties']) for node in node_types)
    total_functions = sum(len(node['functions']) for node in node_types)
    
    for category, nodes in sorted(categories.items()):
        for node in sorted(nodes, key=lambda x: x['name']):
            pass


def print_detailed_node_info():
    node_types = get_all_geometry_node_types()
    
    for i, node in enumerate(sorted(node_types, key=lambda x: x['name']), 1):
        pass


def export_to_json(filename='/tmp/geometry_nodes_detailed_export.json', include_methods=True):
    """Exports detailed information to a JSON file with advanced options"""
    import os
    from datetime import datetime
    
    try:
        node_types = get_all_geometry_node_types()
        
        if include_methods:
            for node in node_types:
                try:
                    node_class = getattr(bpy.types, node['type'])
                    detailed_analysis = analyze_node_detailed(node_class)
                    node.update(detailed_analysis)
                except Exception as e:
                    pass
        
        categories = {}
        for node in node_types:
            category = categorize_node(node['type'])
            if category not in categories:
                categories[category] = []
            categories[category].append(node)
        
        stats = {
            'total_nodes': len(node_types),
            'total_inputs': sum(len(node['inputs']) for node in node_types),
            'total_outputs': sum(len(node['outputs']) for node in node_types),
            'total_properties': sum(len(node['properties']) for node in node_types),
            'total_functions': sum(len(node['functions']) for node in node_types),
            'categories_count': {cat: len(nodes) for cat, nodes in categories.items()},
            'nodes_with_inputs': sum(1 for node in node_types if len(node['inputs']) > 0),
            'nodes_with_outputs': sum(1 for node in node_types if len(node['outputs']) > 0),
            'nodes_with_properties': sum(1 for node in node_types if len(node['properties']) > 0),
            'nodes_with_functions': sum(1 for node in node_types if len(node['functions']) > 0),
            'average_properties_per_node': sum(len(node['properties']) for node in node_types) / len(node_types) if node_types else 0,
            'average_functions_per_node': sum(len(node['functions']) for node in node_types) / len(node_types) if node_types else 0
        }
        
        category_analysis = {}
        for cat_name, nodes in categories.items():
            category_analysis[cat_name] = {
                'count': len(nodes),
                'total_inputs': sum(len(node['inputs']) for node in nodes),
                'total_outputs': sum(len(node['outputs']) for node in nodes),
                'total_properties': sum(len(node['properties']) for node in nodes),
                'total_functions': sum(len(node['functions']) for node in nodes),
                'avg_properties': sum(len(node['properties']) for node in nodes) / len(nodes) if nodes else 0,
                'avg_functions': sum(len(node['functions']) for node in nodes) / len(nodes) if nodes else 0,
                'node_names': [node['name'] for node in nodes[:5]]
            }
        
        export_data = {
            'metadata': {
                'blender_version': bpy.app.version_string,
                'blender_version_tuple': list(bpy.app.version),
                'export_date': datetime.now().isoformat(),
                'export_timestamp': datetime.now().timestamp(),
                'script_version': '2.1 - Advanced Analysis',
                'include_detailed_methods': include_methods,
                'file_size_warning': 'This file may be large due to detailed analysis'
            },
            'summary_statistics': stats,
            'category_analysis': category_analysis,
            'geometry_nodes_by_category': categories,
            'all_geometry_nodes': node_types,
            'export_info': {
                'total_file_sections': 4,
                'largest_category': max(categories.keys(), key=lambda k: len(categories[k])) if categories else None,
                'smallest_category': min(categories.keys(), key=lambda k: len(categories[k])) if categories else None
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(filename)
        
        return filename
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


def create_summary_json(filename='/tmp/geometry_nodes_summary.json'):
    try:
        from datetime import datetime
        
        node_types = get_all_geometry_node_types()
        
        summary_nodes = []
        for node in node_types:
            summary_nodes.append({
                'name': node['name'],
                'type': node['type'],
                'category': categorize_node(node['type']),
                'description': node['description'][:100] if len(node['description']) > 100 else node['description'],
                'input_count': len(node['inputs']),
                'output_count': len(node['outputs']),
                'property_count': len(node['properties']),
                'function_count': len(node['functions'])
            })
        
        categories = {}
        for node in summary_nodes:
            cat = node['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(node)
        
        summary_data = {
            'metadata': {
                'blender_version': bpy.app.version_string,
                'export_date': datetime.now().isoformat(),
                'type': 'summary',
                'description': 'Summary of Blender Geometry Nodes'
            },
            'totals': {
                'nodes': len(summary_nodes),
                'categories': len(categories),
                'total_inputs': sum(node['input_count'] for node in summary_nodes),
                'total_outputs': sum(node['output_count'] for node in summary_nodes),
                'total_properties': sum(node['property_count'] for node in summary_nodes),
                'total_functions': sum(node['function_count'] for node in summary_nodes)
            },
            'categories': {cat: len(nodes) for cat, nodes in categories.items()},
            'nodes': summary_nodes
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return filename
        
    except Exception as e:
        return None


def export_json_by_category(base_path='/tmp/geometry_nodes_categories'):
    try:
        import os
        os.makedirs(base_path, exist_ok=True)
        
        node_types = get_all_geometry_node_types()
        categories = categorize_nodes(node_types)
        
        exported_files = []
        total_size = 0
        
        for category, nodes in categories.items():
            if not nodes:
                continue
                
            safe_category = category.lower().replace(' ', '_').replace('/', '_')
            filename = f"{base_path}/{safe_category}_nodes.json"
            
            detailed_nodes = []
            for node in nodes:
                try:
                    node_class = getattr(bpy.types, node['type'])
                    
                    inputs, outputs = analyze_node_sockets(node_class)
                    properties, _ = get_node_properties(node_class)
                    methods = []
                    for attr_name in dir(node_class):
                        if not attr_name.startswith('_') and callable(getattr(node_class, attr_name, None)):
                            methods.append({'name': attr_name, 'type': 'method'})
                    
                    detailed_node = {
                        'name': node['name'],
                        'type': node['type'],
                        'description': node['description'],
                        'category': category,
                        'inputs': inputs,
                        'outputs': outputs,
                        'properties': properties,
                        'methods': methods,
                        'bl_rna_name': getattr(node_class.bl_rna, 'name', 'N/A') if hasattr(node_class, 'bl_rna') else 'N/A'
                    }
                    detailed_nodes.append(detailed_node)
                    
                except Exception as e:
                    detailed_nodes.append({
                        'name': node['name'],
                        'type': node['type'],
                        'description': node['description'],
                        'category': category,
                        'error': str(e)
                    })
            
            category_data = {
                'category_info': {
                    'name': category,
                    'total_nodes': len(detailed_nodes),
                    'export_timestamp': str(bpy.app.version),
                    'blender_version': bpy.app.version_string
                },
                'nodes': detailed_nodes,
                'statistics': {
                    'nodes_with_inputs': len([n for n in detailed_nodes if n.get('inputs')]),
                    'nodes_with_outputs': len([n for n in detailed_nodes if n.get('outputs')]),
                    'nodes_with_properties': len([n for n in detailed_nodes if n.get('properties')]),
                    'nodes_with_methods': len([n for n in detailed_nodes if n.get('methods')]),
                    'average_properties_per_node': sum(len(n.get('properties', [])) for n in detailed_nodes) / len(detailed_nodes) if detailed_nodes else 0
                }
            }
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(category_data, f, indent=2, ensure_ascii=False)
                
                file_size = os.path.getsize(filename)
                total_size += file_size
                exported_files.append({
                    'category': category,
                    'filename': filename,
                    'size': file_size,
                    'node_count': len(detailed_nodes)
                })
                
            except Exception as e:
                pass
        
        index_data = {
            'export_info': {
                'total_categories': len(exported_files),
                'total_files': len(exported_files),
                'total_size_bytes': total_size,
                'export_timestamp': str(bpy.app.version),
                'blender_version': bpy.app.version_string,
                'base_path': base_path
            },
            'files': exported_files,
            'category_summary': {f['category']: f['node_count'] for f in exported_files}
        }
        
        index_filename = f"{base_path}/index.json"
        with open(index_filename, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        return exported_files
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


def analyze_node_detailed(node_class):
    detailed_info = {
        'methods': [],
        'class_attributes': [],
        'socket_info': {},
        'bl_rna_details': {}
    }
    
    try:
        for attr_name in dir(node_class):
            if not attr_name.startswith('_') and callable(getattr(node_class, attr_name, None)):
                method = getattr(node_class, attr_name)
                detailed_info['methods'].append({
                    'name': attr_name,
                    'doc': getattr(method, '__doc__', 'No documentation'),
                    'type': 'method'
                })
        
        for attr_name in dir(node_class):
            if not attr_name.startswith('_') and not callable(getattr(node_class, attr_name, None)):
                attr_value = getattr(node_class, attr_name, None)
                detailed_info['class_attributes'].append({
                    'name': attr_name,
                    'value': str(attr_value)[:100] if attr_value else 'None',
                    'type': type(attr_value).__name__
                })
        
        if hasattr(node_class, 'bl_rna'):
            bl_rna = node_class.bl_rna
            detailed_info['bl_rna_details'] = {
                'identifier': getattr(bl_rna, 'identifier', 'N/A'),
                'name': getattr(bl_rna, 'name', 'N/A'),
                'description': getattr(bl_rna, 'description', 'N/A'),
                'base': getattr(bl_rna, 'base', {}).name if hasattr(getattr(bl_rna, 'base', {}), 'name') else 'N/A'
            }
    
    except Exception as e:
        detailed_info['error'] = str(e)
    
    return detailed_info


def search_nodes_by_keyword(keyword):
    """Searches geometry nodes by keyword"""
    keyword = keyword.lower()
    node_types = get_all_geometry_node_types()
    results = []
    
    for node in node_types:
        if (keyword in node['name'].lower() or 
            keyword in node['type'].lower() or 
            keyword in node['description'].lower()):
            results.append(node)
    
    return results


def search_by_property_type(prop_type):
    """Searches nodes that have properties of a specific type"""
    node_types = get_all_geometry_node_types()
    results = []
    
    for node in node_types:
        for prop in node['properties']:
            if prop['type'] == prop_type:
                results.append({
                    'node': node,
                    'matching_properties': [p for p in node['properties'] if p['type'] == prop_type]
                })
                break
    
    return results


def search_by_function(func_name):
    """Searches nodes that have functions with a specific name"""
    node_types = get_all_geometry_node_types()
    results = []
    
    for node in node_types:
        for func in node['functions']:
            if func_name.lower() in func['name'].lower():
                results.append({
                    'node': node,
                    'matching_functions': [f for f in node['functions'] if func_name.lower() in f['name'].lower()]
                })
                break
    
    return results


def print_search_results(keyword):
    results = search_nodes_by_keyword(keyword)
    
    if not results:
        return
    
    for i, node in enumerate(results, 1):
        category = categorize_node(node['type'])


def generate_advanced_statistics():
    """Generates advanced statistics about the geometry nodes"""
    node_types = get_all_geometry_node_types()
    
    stats = {
        'property_types': {},
        'function_patterns': {},
        'most_complex_nodes': [],
        'input_output_analysis': {},
        'category_distribution': {}
    }
    
    for node in node_types:
        for prop in node['properties']:
            prop_type = prop['type']
            if prop_type not in stats['property_types']:
                stats['property_types'][prop_type] = 0
            stats['property_types'][prop_type] += 1
    
    for node in node_types:
        for func in node['functions']:
            func_name = func['name']
            if func_name not in stats['function_patterns']:
                stats['function_patterns'][func_name] = 0
            stats['function_patterns'][func_name] += 1
    
    complexity_scores = []
    for node in node_types:
        complexity = len(node['properties']) + len(node['functions']) + len(node['inputs']) + len(node['outputs'])
        complexity_scores.append({
            'node': node['name'],
            'type': node['type'],
            'complexity': complexity,
            'properties': len(node['properties']),
            'functions': len(node['functions']),
            'inputs': len(node['inputs']),
            'outputs': len(node['outputs'])
        })
    
    stats['most_complex_nodes'] = sorted(complexity_scores, key=lambda x: x['complexity'], reverse=True)[:10]
    
    for node in node_types:
        input_count = len(node['inputs'])
        output_count = len(node['outputs'])
        key = f"{input_count}in_{output_count}out"
        if key not in stats['input_output_analysis']:
            stats['input_output_analysis'][key] = 0
        stats['input_output_analysis'][key] += 1
    
    for node in node_types:
        category = categorize_node(node['type'])
        if category not in stats['category_distribution']:
            stats['category_distribution'][category] = 0
        stats['category_distribution'][category] += 1
    
    return stats


def print_advanced_statistics():
    stats = generate_advanced_statistics()


def demo_advanced_search():
    float_results = search_by_property_type('FLOAT')
    update_results = search_by_function('update')


def main():
    try:
        node_types = get_all_geometry_node_types()
        
        print_geometry_nodes_summary()
        print_advanced_statistics()
        demo_advanced_search()
        
        detailed_file = export_to_json('/tmp/geometry_nodes_detailed_complete.json', include_methods=True)
        summary_file = create_summary_json('/tmp/geometry_nodes_summary.json')
        basic_file = export_to_json('/tmp/geometry_nodes_basic.json', include_methods=False)
        category_files = export_json_by_category('/tmp/geometry_nodes_categories')
        
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        import bpy
        main()
    except ImportError:
        pass