#!/usr/bin/env python3
"""
Comprehensive Geometry Nodes Analysis Script for Blender
Execute inside Blender: blender --python tanuki.py
Dependencies: bpy, json only
Features: Real socket extraction, categorized export, detailed analysis
"""

try:
    import bpy
    import json
    import os
    from datetime import datetime
    
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
    
    def analyze_node_basics(node_class):
        """Basic analysis of node properties and functions"""
        properties_count = 0
        functions_count = 0
        
        try:
            if hasattr(node_class, 'bl_rna'):
                bl_rna = node_class.bl_rna
                
                # Count properties (excluding internal ones)
                if hasattr(bl_rna, 'properties'):
                    properties_count = len([p for p in bl_rna.properties 
                                          if not p.identifier.startswith('bl_') 
                                          and not p.identifier.startswith('rna_')])
                
                # Count functions
                if hasattr(bl_rna, 'functions'):
                    functions_count = len(bl_rna.functions)
                    
        except Exception:
            pass
        
        return properties_count, functions_count
    
    def convert_vector_for_json(value):
        """Convert Blender Vector objects to lists for JSON serialization"""
        if hasattr(value, '__iter__') and not isinstance(value, str):
            try:
                # Try to convert to list (works for Vector, Color, etc.)
                return list(value)
            except:
                try:
                    # If list conversion fails, try to get length and individual elements
                    if hasattr(value, '__len__'):
                        return [float(value[i]) for i in range(len(value))]
                    else:
                        return str(value)
                except:
                    return str(value)
        return value

    def get_real_geometry_node_sockets(node_type):
        """Extract real socket information by instantiating the node in Blender"""
        inputs = []
        outputs = []
        
        try:
            # Create temporary geometry node tree
            temp_tree_name = "temp_socket_analysis"
            
            # Clean up any existing temp tree
            if temp_tree_name in bpy.data.node_groups:
                bpy.data.node_groups.remove(bpy.data.node_groups[temp_tree_name])
            
            # Create new node tree
            node_tree = bpy.data.node_groups.new(temp_tree_name, 'GeometryNodeTree')
            
            # Add the node to analyze
            node = node_tree.nodes.new(type=node_type)
            
            # Extract input sockets
            for socket in node.inputs:
                socket_info = {
                    "name": socket.name,
                    "identifier": socket.identifier,
                    "type": socket.type,
                    "description": f"{socket.name} socket",
                    "socket_type": "INPUT"
                }
                
                # Try to get default value
                try:
                    if hasattr(socket, 'default_value'):
                        default_val = socket.default_value
                        # Handle different types of default values
                        if hasattr(default_val, '__iter__') and not isinstance(default_val, str):
                            # For Vector, Color, etc.
                            socket_info["default_value"] = [float(x) for x in default_val]
                        elif hasattr(default_val, 'x') and hasattr(default_val, 'y'):
                            # For Vector-like objects with x, y, z attributes
                            if hasattr(default_val, 'z'):
                                socket_info["default_value"] = [float(default_val.x), float(default_val.y), float(default_val.z)]
                            else:
                                socket_info["default_value"] = [float(default_val.x), float(default_val.y)]
                        else:
                            socket_info["default_value"] = default_val
                except Exception as e:
                    # Skip default value if conversion fails
                    pass
                
                inputs.append(socket_info)
            
            # Extract output sockets
            for socket in node.outputs:
                socket_info = {
                    "name": socket.name,
                    "identifier": socket.identifier,
                    "type": socket.type,
                    "description": f"{socket.name} output socket",
                    "socket_type": "OUTPUT"
                }
                outputs.append(socket_info)
            
            # Clean up temp tree
            bpy.data.node_groups.remove(node_tree)
            
            # Success message for important nodes
            if inputs or outputs:
                print(f"✓ {node_type}: {len(inputs)} inputs, {len(outputs)} outputs")
            
        except Exception as e:
            # Fallback to property analysis if real node analysis fails
            print(f"⚠ {node_type}: Real analysis failed, using fallback")
            return analyze_node_sockets_fallback(node_type)
        
        return inputs, outputs

    def analyze_node_sockets_fallback(node_type):
        """Fallback socket analysis when real node instantiation fails"""
        inputs = []
        outputs = []
        
        # Basic fallback patterns based on node type
        if 'Input' in node_type:
            outputs = [{'name': 'Value', 'type': 'VALUE', 'socket_type': 'OUTPUT'}]
        elif 'Output' in node_type:
            inputs = [{'name': 'Geometry', 'type': 'GEOMETRY', 'socket_type': 'INPUT'}]
        elif 'Mesh' in node_type:
            inputs = [{'name': 'Mesh', 'type': 'GEOMETRY', 'socket_type': 'INPUT'}]
            outputs = [{'name': 'Mesh', 'type': 'GEOMETRY', 'socket_type': 'OUTPUT'}]
        elif 'Curve' in node_type:
            inputs = [{'name': 'Curve', 'type': 'GEOMETRY', 'socket_type': 'INPUT'}]
            outputs = [{'name': 'Curve', 'type': 'GEOMETRY', 'socket_type': 'OUTPUT'}]
        else:
            # Generic geometry node
            inputs = [{'name': 'Geometry', 'type': 'GEOMETRY', 'socket_type': 'INPUT'}]
            outputs = [{'name': 'Geometry', 'type': 'GEOMETRY', 'socket_type': 'OUTPUT'}]
        
        return inputs, outputs

    def analyze_node_sockets_simple(node_class, node_type):
        """Analyzes inputs and outputs for geometry nodes with real socket detection"""
        # Try to get real socket information first
        try:
            inputs, outputs = get_real_geometry_node_sockets(node_type)
            if inputs or outputs:
                return inputs, outputs
        except Exception as e:
            print(f"Real socket analysis failed for {node_type}: {e}")
        
        # Fallback to basic analysis
        return analyze_node_sockets_fallback(node_type)
    
    def get_detailed_node_info(node_class, node_type):
        """Gets detailed node information including inputs, outputs, properties and functions"""
        detailed_info = {
            'inputs': [],
            'outputs': [],
            'properties': [],
            'methods': [],
            'bl_rna_name': '',
            'socket_source': 'real_node_analysis'
        }
        
        # Analyze inputs and outputs using real socket detection
        inputs, outputs = analyze_node_sockets_simple(node_class, node_type)
        detailed_info['inputs'] = inputs
        detailed_info['outputs'] = outputs
        
        try:
            if hasattr(node_class, 'bl_rna'):
                bl_rna = node_class.bl_rna
                detailed_info['bl_rna_name'] = getattr(bl_rna, 'name', node_type)
                
                # Properties analysis
                if hasattr(bl_rna, 'properties'):
                    for prop in bl_rna.properties:
                        if not prop.identifier.startswith('bl_') and not prop.identifier.startswith('rna_'):
                            prop_info = {
                                'name': prop.name or prop.identifier,
                                'identifier': prop.identifier,
                                'type': prop.type,
                                'description': getattr(prop, 'description', ''),
                                'default': getattr(prop, 'default', 'N/A'),
                                'is_readonly': getattr(prop, 'is_readonly', False)
                            }
                            
                            # Add type-specific information
                            if hasattr(prop, 'min') and hasattr(prop, 'max'):
                                prop_info['min'] = getattr(prop, 'min', None)
                                prop_info['max'] = getattr(prop, 'max', None)
                            
                            if hasattr(prop, 'enum_items'):
                                prop_info['enum_items'] = [item.identifier for item in prop.enum_items]
                            
                            detailed_info['properties'].append(prop_info)
                
                # Methods analysis
                if hasattr(bl_rna, 'functions'):
                    for func in bl_rna.functions:
                        func_info = {
                            'name': func.identifier,
                            'type': 'method'
                        }
                        detailed_info['methods'].append(func_info)
                        
        except Exception as e:
            print(f"Error analyzing {node_type}: {e}")
            # Mark as fallback analysis if real analysis failed
            detailed_info['socket_source'] = 'property_analysis'
        
        return detailed_info
    
    def get_all_geometry_nodes(include_detailed=False):
        """Gets all available geometry nodes with basic or detailed information"""
        geometry_nodes = []
        
        # Search for all types starting with 'GeometryNode'
        for attr_name in dir(bpy.types):
            if attr_name.startswith('GeometryNode'):
                try:
                    node_class = getattr(bpy.types, attr_name)
                    if hasattr(node_class, 'bl_rna'):
                        name = getattr(node_class.bl_rna, 'name', attr_name)
                        description = getattr(node_class.bl_rna, 'description', 'No description')
                        
                        # Basic analysis
                        prop_count, func_count = analyze_node_basics(node_class)
                        
                        node_info = {
                            'name': name,
                            'type': attr_name,
                            'description': description,
                            'category': categorize_node(attr_name),
                            'properties_count': prop_count,
                            'functions_count': func_count
                        }
                        
                        # Detailed information if requested
                        if include_detailed:
                            detailed_info = get_detailed_node_info(node_class, attr_name)
                            node_info.update(detailed_info)
                        
                        geometry_nodes.append(node_info)
                except Exception as e:
                    print(f"Error processing {attr_name}: {e}")
        
        return geometry_nodes
    
    def list_geometry_nodes():
        """Lists all available geometry nodes organized by categories"""
        print("=" * 60)
        print("AVAILABLE GEOMETRY NODES IN BLENDER")
        print("=" * 60)
        print(f"Blender Version: {bpy.app.version_string}")
        
        geometry_nodes = get_all_geometry_nodes()
        
        # Group by categories
        categories = {}
        for node in geometry_nodes:
            category = node['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(node)
        
        print(f"\nTotal Geometry Nodes found: {len(geometry_nodes)}\n")
        
        # General statistics
        total_properties = sum(node['properties_count'] for node in geometry_nodes)
        total_functions = sum(node['functions_count'] for node in geometry_nodes)
        total_inputs = 0
        total_outputs = 0
        
        # Count sockets if detailed info is available
        for node in geometry_nodes:
            if 'inputs' in node:
                total_inputs += len(node['inputs'])
            if 'outputs' in node:
                total_outputs += len(node['outputs'])
        
        print(f"📊 Summary: {total_properties} properties, {total_functions} functions")
        if total_inputs > 0 or total_outputs > 0:
            print(f"🔌 Sockets: {total_inputs} inputs, {total_outputs} outputs")
        
        # Print by categories
        for category, nodes in sorted(categories.items()):
            cat_props = sum(node['properties_count'] for node in nodes)
            cat_funcs = sum(node['functions_count'] for node in nodes)
            cat_inputs = sum(len(node.get('inputs', [])) for node in nodes)
            cat_outputs = sum(len(node.get('outputs', [])) for node in nodes)
            
            print(f"\n{'='*15} {category.upper()} ({len(nodes)} nodes) {'='*15}")
            print(f"Properties: {cat_props}, Functions: {cat_funcs}")
            if cat_inputs > 0 or cat_outputs > 0:
                print(f"Sockets: {cat_inputs} inputs, {cat_outputs} outputs")
            
            for node in sorted(nodes, key=lambda x: x['name']):
                print(f"  • {node['name']}")
                print(f"    Type: {node['type']}")
                if len(node['description']) < 80:
                    print(f"    Description: {node['description']}")
                
                # Show counts if it has properties or functions
                if node['properties_count'] > 0 or node['functions_count'] > 0:
                    print(f"    ⚙️ Props: {node['properties_count']}, 🔧 Funcs: {node['functions_count']}")
                print()
        
        return geometry_nodes
    
    def search_nodes(keyword):
        """Search nodes by keyword"""
        keyword = keyword.lower()
        all_nodes = get_all_geometry_nodes()
        results = []
        
        for node in all_nodes:
            if (keyword in node['name'].lower() or 
                keyword in node['type'].lower() or 
                keyword in node['description'].lower()):
                results.append(node)
        
        return results
    
    def save_nodes_by_category(base_path='geometry_nodes_categories'):
        """Save geometry nodes to separate JSON files by category"""
        print(f"\n📁 Exporting by categories to: {base_path}/")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(base_path, exist_ok=True)
            
            # Get all nodes with detailed information
            all_nodes = get_all_geometry_nodes(include_detailed=True)
            
            # Group by categories
            categories = {}
            for node in all_nodes:
                category = node['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(node)
            
            exported_files = []
            total_size = 0
            
            # Export each category
            for category, nodes in categories.items():
                # Create safe filename
                safe_category = category.lower().replace(' ', '_')
                filename = os.path.join(base_path, f"{safe_category}_nodes.json")
                
                # Calculate socket statistics
                total_inputs = sum(len(node.get('inputs', [])) for node in nodes)
                total_outputs = sum(len(node.get('outputs', [])) for node in nodes)
                
                # Data for this category
                category_data = {
                    'category_info': {
                        'name': category,
                        'total_nodes': len(nodes),
                        'export_date': datetime.now().isoformat(),
                        'blender_version': bpy.app.version_string
                    },
                    'statistics': {
                        'total_properties': sum(node['properties_count'] for node in nodes),
                        'total_functions': sum(node['functions_count'] for node in nodes),
                        'total_inputs': total_inputs,
                        'total_outputs': total_outputs,
                        'average_properties': sum(node['properties_count'] for node in nodes) / len(nodes) if nodes else 0,
                        'average_functions': sum(node['functions_count'] for node in nodes) / len(nodes) if nodes else 0
                    },
                    'nodes': nodes
                }
                
                # Save file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(category_data, f, indent=2, ensure_ascii=False)
                
                file_size = os.path.getsize(filename)
                total_size += file_size
                
                exported_files.append({
                    'category': category,
                    'filename': filename,
                    'size': file_size,
                    'node_count': len(nodes)
                })
                
                print(f"  ✅ {category}: {len(nodes)} nodes → {filename} ({file_size:,} bytes)")
            
            # Create index file
            index_data = {
                'export_info': {
                    'total_categories': len(exported_files),
                    'total_files': len(exported_files),
                    'total_size_bytes': total_size,
                    'total_nodes': len(all_nodes),
                    'export_date': datetime.now().isoformat(),
                    'blender_version': bpy.app.version_string
                },
                'files': exported_files,
                'category_summary': {f['category']: f['node_count'] for f in exported_files}
            }
            
            index_filename = os.path.join(base_path, 'index.json')
            with open(index_filename, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 Summary:")
            print(f"  • {len(exported_files)} categories exported")
            print(f"  • Total size: {total_size:,} bytes")
            print(f"  • Index file: {index_filename}")
            
            return exported_files
            
        except Exception as e:
            print(f"❌ Error exporting by categories: {e}")
            return None

    def save_nodes_to_json(output_path=None, include_detailed=True):
        """Save geometry nodes to a JSON file"""
        if output_path is None:
            # Use current directory or tmp
            try:
                output_path = os.path.join(os.getcwd(), 'geometry_nodes_export.json')
            except:
                output_path = '/tmp/geometry_nodes_export.json'
        
        print(f"\n📁 Exporting data to: {output_path}")
        
        try:
            # Get all nodes with detailed information
            all_nodes = get_all_geometry_nodes(include_detailed=include_detailed)
            
            # Create data structure for export
            export_data = {
                'metadata': {
                    'blender_version': bpy.app.version_string,
                    'blender_version_tuple': list(bpy.app.version),
                    'export_date': datetime.now().isoformat(),
                    'total_nodes': len(all_nodes),
                    'include_detailed_info': include_detailed,
                    'socket_analysis': 'real_node_analysis' if include_detailed else 'basic'
                },
                'summary': {
                    'total_properties': sum(node['properties_count'] for node in all_nodes),
                    'total_functions': sum(node['functions_count'] for node in all_nodes),
                    'total_inputs': sum(len(node.get('inputs', [])) for node in all_nodes),
                    'total_outputs': sum(len(node.get('outputs', [])) for node in all_nodes),
                    'categories': {}
                },
                'nodes': all_nodes
            }
            
            # Generate statistics by category
            categories = {}
            for node in all_nodes:
                category = node['category']
                if category not in categories:
                    categories[category] = {
                        'count': 0,
                        'properties_count': 0,
                        'functions_count': 0,
                        'inputs_count': 0,
                        'outputs_count': 0
                    }
                categories[category]['count'] += 1
                categories[category]['properties_count'] += node['properties_count']
                categories[category]['functions_count'] += node['functions_count']
                categories[category]['inputs_count'] += len(node.get('inputs', []))
                categories[category]['outputs_count'] += len(node.get('outputs', []))
            
            export_data['summary']['categories'] = categories
            
            # Save JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ Export successful!")
            print(f"   📄 File: {output_path}")
            print(f"   📊 Size: {file_size:,} bytes")
            print(f"   🔢 Nodes: {len(all_nodes)}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error exporting JSON: {e}")
            return None
    
    def load_nodes_from_json(json_path):
        """Load geometry nodes from a JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📂 Loaded: {json_path}")
            print(f"🔢 Nodes: {data['metadata']['total_nodes']}")
            print(f"📅 Date: {data['metadata']['export_date']}")
            print(f"🔧 Blender: {data['metadata']['blender_version']}")
            
            return data
            
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return None
    
    def demo_search():
        """Demonstrates search functionality"""
        print("\n" + "=" * 60)
        print("SEARCH DEMO")
        print("=" * 60)
        
        search_terms = ['mesh', 'curve', 'instance', 'attribute', 'transform']
        
        for term in search_terms:
            results = search_nodes(term)
            print(f"\n🔍 '{term}' - {len(results)} results:")
            for node in results[:3]:  # Show only first 3
                print(f"  • {node['name']} ({node['category']})")
            if len(results) > 3:
                print(f"  ... and {len(results) - 3} more")
    
    # Execute if imported correctly
    if __name__ == "__main__":
        print("🚀 Starting Geometry Nodes analysis...")
        
        # List nodes in console
        nodes = list_geometry_nodes()
        
        # Search demo
        demo_search()
        
        # Export to JSON
        print("\n" + "=" * 60)
        print("JSON EXPORT")
        print("=" * 60)
        
        # Export basic version
        json_path_basic = save_nodes_to_json(
            output_path='geometry_nodes_basic.json', 
            include_detailed=False
        )
        
        # Export detailed version with real socket analysis
        print("\n🔍 Starting detailed analysis with real socket extraction...")
        json_path_detailed = save_nodes_to_json(
            output_path='geometry_nodes_detailed.json', 
            include_detailed=True
        )
        
        # Export by categories
        print("\n📁 Generating files by categories...")
        category_files = save_nodes_by_category('geometry_nodes_categories')
        
        print(f"\n✅ Analysis completed!")
        print(f"📊 Total: {len(nodes)} geometry nodes")
        print(f"📁 JSON files generated:")
        if json_path_basic:
            print(f"   • Basic: geometry_nodes_basic.json")
        if json_path_detailed:
            print(f"   • Detailed: geometry_nodes_detailed.json")
        
        print("\n💡 Available functions:")
        print("   • search_nodes('keyword') - Search nodes")
        print("   • save_nodes_to_json('file.json') - Export")
        print("   • load_nodes_from_json('file.json') - Import")

except ImportError:
    print("❌ Error: bpy is not available.")
    print("This script must be executed inside Blender:")
    print("  blender --python tanuki.py")
    print("Or from Blender's script editor.")