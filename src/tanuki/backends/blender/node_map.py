"""Auto-generated Blender Geometry Nodes metadata.

DO NOT EDIT MANUALLY — regenerate with:
    python -m tanuki.codegen.generate_nodes

Generated from 223 nodes across 12 category files.
"""

# Maps bpy node type string → full metadata (inputs, outputs, etc.)
NODE_REGISTRY: dict[str, dict] = {
    'GeometryNodeAttributeDomainSize': {
    "name": 'Domain Size',
    "type": 'GeometryNodeAttributeDomainSize',
    "category": 'Attribute',
    "description": 'Retrieve the number of elements in a geometry for each attribute domain',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Point Count', "identifier": 'Point Count', "type": 'INT'},
        {"name": 'Edge Count', "identifier": 'Edge Count', "type": 'INT'},
        {"name": 'Face Count', "identifier": 'Face Count', "type": 'INT'},
        {"name": 'Face Corner Count', "identifier": 'Face Corner Count', "type": 'INT'},
        {"name": 'Spline Count', "identifier": 'Spline Count', "type": 'INT'},
        {"name": 'Instance Count', "identifier": 'Instance Count', "type": 'INT'},
        {"name": 'Layer Count', "identifier": 'Layer Count', "type": 'INT'}
    ],
},
    'GeometryNodeAttributeStatistic': {
    "name": 'Attribute Statistic',
    "type": 'GeometryNodeAttributeStatistic',
    "category": 'Attribute',
    "description": 'Calculate statistics about a data set from a field evaluated on a geometry',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Attribute', "identifier": 'Attribute', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Mean', "identifier": 'Mean', "type": 'VALUE'},
        {"name": 'Median', "identifier": 'Median', "type": 'VALUE'},
        {"name": 'Sum', "identifier": 'Sum', "type": 'VALUE'},
        {"name": 'Min', "identifier": 'Min', "type": 'VALUE'},
        {"name": 'Max', "identifier": 'Max', "type": 'VALUE'},
        {"name": 'Range', "identifier": 'Range', "type": 'VALUE'},
        {"name": 'Standard Deviation', "identifier": 'Standard Deviation', "type": 'VALUE'},
        {"name": 'Variance', "identifier": 'Variance', "type": 'VALUE'}
    ],
},
    'GeometryNodeBlurAttribute': {
    "name": 'Blur Attribute',
    "type": 'GeometryNodeBlurAttribute',
    "category": 'Attribute',
    "description": 'Mix attribute values of neighboring elements',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Iterations', "identifier": 'Iterations', "type": 'INT', "default_value": 1},
        {"name": 'Weight', "identifier": 'Weight', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeCaptureAttribute': {
    "name": 'Capture Attribute',
    "type": 'GeometryNodeCaptureAttribute',
    "category": 'Attribute',
    "description": 'Store the result of a field on a geometry and output the data as a node socket. Allows remembering or interpolating data as the geometry changes, such as positions before deformation',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeRemoveAttribute': {
    "name": 'Remove Named Attribute',
    "type": 'GeometryNodeRemoveAttribute',
    "category": 'Attribute',
    "description": 'Delete an attribute with a specified name from a geometry. Typically used to optimize performance',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeStoreNamedAttribute': {
    "name": 'Store Named Attribute',
    "type": 'GeometryNodeStoreNamedAttribute',
    "category": 'Attribute',
    "description": 'Store the result of a field on a geometry as an attribute with the specified name',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''},
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetGreasePencilColor': {
    "name": 'Set Grease Pencil Color',
    "type": 'GeometryNodeSetGreasePencilColor',
    "category": 'Color',
    "description": 'Set color and opacity attributes on Grease Pencil geometry',
    "inputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Color', "identifier": 'Color', "type": 'RGBA', "default_value": [1.0, 1.0, 1.0, 1.0]},
        {"name": 'Opacity', "identifier": 'Opacity', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveArc': {
    "name": 'Arc',
    "type": 'GeometryNodeCurveArc',
    "category": 'Curve',
    "description": 'Generate a poly spline arc',
    "inputs": [
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT', "default_value": 16},
        {"name": 'Start', "identifier": 'Start', "type": 'VECTOR', "default_value": [-1.0, 0.0, 0.0]},
        {"name": 'Middle', "identifier": 'Middle', "type": 'VECTOR', "default_value": [0.0, 2.0, 0.0]},
        {"name": 'End', "identifier": 'End', "type": 'VECTOR', "default_value": [1.0, 0.0, 0.0]},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Start Angle', "identifier": 'Start Angle', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Sweep Angle', "identifier": 'Sweep Angle', "type": 'VALUE', "default_value": 5.497786998748779},
        {"name": 'Offset Angle', "identifier": 'Offset Angle', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Connect Center', "identifier": 'Connect Center', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Invert Arc', "identifier": 'Invert Arc', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Center', "identifier": 'Center', "type": 'VECTOR'},
        {"name": 'Normal', "identifier": 'Normal', "type": 'VECTOR'},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE'}
    ],
},
    'GeometryNodeCurveEndpointSelection': {
    "name": 'Endpoint Selection',
    "type": 'GeometryNodeCurveEndpointSelection',
    "category": 'Curve',
    "description": 'Provide a selection for an arbitrary number of endpoints in each spline',
    "inputs": [
        {"name": 'Start Size', "identifier": 'Start Size', "type": 'INT', "default_value": 1},
        {"name": 'End Size', "identifier": 'End Size', "type": 'INT', "default_value": 1}
    ],
    "outputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeCurveHandleTypeSelection': {
    "name": 'Handle Type Selection',
    "type": 'GeometryNodeCurveHandleTypeSelection',
    "category": 'Curve',
    "description": 'Provide a selection based on the handle types of Bézier control points',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeCurveLength': {
    "name": 'Curve Length',
    "type": 'GeometryNodeCurveLength',
    "category": 'Curve',
    "description": 'Retrieve the length of all splines added together',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE'}
    ],
},
    'GeometryNodeCurveOfPoint': {
    "name": 'Curve of Point',
    "type": 'GeometryNodeCurveOfPoint',
    "category": 'Curve',
    "description": 'Retrieve the curve a control point is part of',
    "inputs": [
        {"name": 'Point Index', "identifier": 'Point Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Curve Index', "identifier": 'Curve Index', "type": 'INT'},
        {"name": 'Index in Curve', "identifier": 'Index in Curve', "type": 'INT'}
    ],
},
    'GeometryNodeCurvePrimitiveBezierSegment': {
    "name": 'Bézier Segment',
    "type": 'GeometryNodeCurvePrimitiveBezierSegment',
    "category": 'Curve',
    "description": 'Generate a 2D Bézier spline from the given control points and handles',
    "inputs": [
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT', "default_value": 16},
        {"name": 'Start', "identifier": 'Start', "type": 'VECTOR', "default_value": [-1.0, 0.0, 0.0]},
        {"name": 'Start Handle', "identifier": 'Start Handle', "type": 'VECTOR', "default_value": [-0.5, 0.5, 0.0]},
        {"name": 'End Handle', "identifier": 'End Handle', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'End', "identifier": 'End', "type": 'VECTOR', "default_value": [1.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurvePrimitiveCircle': {
    "name": 'Curve Circle',
    "type": 'GeometryNodeCurvePrimitiveCircle',
    "category": 'Curve',
    "description": 'Generate a poly spline circle',
    "inputs": [
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT', "default_value": 32},
        {"name": 'Point 1', "identifier": 'Point 1', "type": 'VECTOR', "default_value": [-1.0, 0.0, 0.0]},
        {"name": 'Point 2', "identifier": 'Point 2', "type": 'VECTOR', "default_value": [0.0, 1.0, 0.0]},
        {"name": 'Point 3', "identifier": 'Point 3', "type": 'VECTOR', "default_value": [1.0, 0.0, 0.0]},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Center', "identifier": 'Center', "type": 'VECTOR'}
    ],
},
    'GeometryNodeCurvePrimitiveLine': {
    "name": 'Curve Line',
    "type": 'GeometryNodeCurvePrimitiveLine',
    "category": 'Curve',
    "description": 'Generate a poly spline line with two points',
    "inputs": [
        {"name": 'Start', "identifier": 'Start', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'End', "identifier": 'End', "type": 'VECTOR', "default_value": [0.0, 0.0, 1.0]},
        {"name": 'Direction', "identifier": 'Direction', "type": 'VECTOR', "default_value": [0.0, 0.0, 1.0]},
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurvePrimitiveQuadrilateral': {
    "name": 'Quadrilateral',
    "type": 'GeometryNodeCurvePrimitiveQuadrilateral',
    "category": 'Curve',
    "description": 'Generate a polygon with four points',
    "inputs": [
        {"name": 'Width', "identifier": 'Width', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Height', "identifier": 'Height', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Bottom Width', "identifier": 'Bottom Width', "type": 'VALUE', "default_value": 4.0},
        {"name": 'Top Width', "identifier": 'Top Width', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Offset', "identifier": 'Offset', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Bottom Height', "identifier": 'Bottom Height', "type": 'VALUE', "default_value": 3.0},
        {"name": 'Top Height', "identifier": 'Top Height', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Point 1', "identifier": 'Point 1', "type": 'VECTOR', "default_value": [-1.0, -1.0, 0.0]},
        {"name": 'Point 2', "identifier": 'Point 2', "type": 'VECTOR', "default_value": [1.0, -1.0, 0.0]},
        {"name": 'Point 3', "identifier": 'Point 3', "type": 'VECTOR', "default_value": [1.0, 1.0, 0.0]},
        {"name": 'Point 4', "identifier": 'Point 4', "type": 'VECTOR', "default_value": [-1.0, 1.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveQuadraticBezier': {
    "name": 'Quadratic Bézier',
    "type": 'GeometryNodeCurveQuadraticBezier',
    "category": 'Curve',
    "description": 'Generate a poly spline in a parabola shape with control points positions',
    "inputs": [
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT', "default_value": 16},
        {"name": 'Start', "identifier": 'Start', "type": 'VECTOR', "default_value": [-1.0, 0.0, 0.0]},
        {"name": 'Middle', "identifier": 'Middle', "type": 'VECTOR', "default_value": [0.0, 2.0, 0.0]},
        {"name": 'End', "identifier": 'End', "type": 'VECTOR', "default_value": [1.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveSetHandles': {
    "name": 'Set Handle Type',
    "type": 'GeometryNodeCurveSetHandles',
    "category": 'Curve',
    "description": 'Set the handle type for the control points of a Bézier curve',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveSpiral': {
    "name": 'Spiral',
    "type": 'GeometryNodeCurveSpiral',
    "category": 'Curve',
    "description": 'Generate a poly spline in a spiral shape',
    "inputs": [
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT', "default_value": 32},
        {"name": 'Rotations', "identifier": 'Rotations', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Start Radius', "identifier": 'Start Radius', "type": 'VALUE', "default_value": 1.0},
        {"name": 'End Radius', "identifier": 'End Radius', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Height', "identifier": 'Height', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Reverse', "identifier": 'Reverse', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveSplineType': {
    "name": 'Set Spline Type',
    "type": 'GeometryNodeCurveSplineType',
    "category": 'Curve',
    "description": 'Change the type of curves',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveStar': {
    "name": 'Star',
    "type": 'GeometryNodeCurveStar',
    "category": 'Curve',
    "description": 'Generate a poly spline in a star pattern by connecting alternating points of two circles',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'INT', "default_value": 8},
        {"name": 'Inner Radius', "identifier": 'Inner Radius', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Outer Radius', "identifier": 'Outer Radius', "type": 'VALUE', "default_value": 2.0},
        {"name": 'Twist', "identifier": 'Twist', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Outer Points', "identifier": 'Outer Points', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeCurveToPoints': {
    "name": 'Curve to Points',
    "type": 'GeometryNodeCurveToPoints',
    "category": 'Curve',
    "description": 'Generate a point cloud by sampling positions along curves',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Count', "identifier": 'Count', "type": 'INT', "default_value": 10},
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE', "default_value": 0.10000000149011612}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Tangent', "identifier": 'Tangent', "type": 'VECTOR'},
        {"name": 'Normal', "identifier": 'Normal', "type": 'VECTOR'},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION'}
    ],
},
    'GeometryNodeCurvesToGreasePencil': {
    "name": 'Curves to Grease Pencil',
    "type": 'GeometryNodeCurvesToGreasePencil',
    "category": 'Curve',
    "description": 'Convert the curves in each top-level instance into Grease Pencil layer',
    "inputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Instances as Layers', "identifier": 'Instances as Layers', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeDeformCurvesOnSurface': {
    "name": 'Deform Curves on Surface',
    "type": 'GeometryNodeDeformCurvesOnSurface',
    "category": 'Curve',
    "description": "Translate and rotate curves based on changes between the object's original and evaluated surface mesh",
    "inputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeEdgePathsToCurves': {
    "name": 'Edge Paths to Curves',
    "type": 'GeometryNodeEdgePathsToCurves',
    "category": 'Curve',
    "description": 'Output curves following paths across mesh edges',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Start Vertices', "identifier": 'Start Vertices', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Next Vertex Index', "identifier": 'Next Vertex Index', "type": 'INT', "default_value": -1}
    ],
    "outputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeFillCurve': {
    "name": 'Fill Curve',
    "type": 'GeometryNodeFillCurve',
    "category": 'Curve',
    "description": 'Generate a mesh on the XY plane with faces on the inside of input curves',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeFilletCurve': {
    "name": 'Fillet Curve',
    "type": 'GeometryNodeFilletCurve',
    "category": 'Curve',
    "description": 'Round corners by generating circular arcs on each control point',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Count', "identifier": 'Count', "type": 'INT', "default_value": 1},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.25},
        {"name": 'Limit Radius', "identifier": 'Limit Radius', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeGreasePencilToCurves': {
    "name": 'Grease Pencil to Curves',
    "type": 'GeometryNodeGreasePencilToCurves',
    "category": 'Curve',
    "description": 'Convert Grease Pencil layers into curve instances',
    "inputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Layers as Instances', "identifier": 'Layers as Instances', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeInterpolateCurves': {
    "name": 'Interpolate Curves',
    "type": 'GeometryNodeInterpolateCurves',
    "category": 'Curve',
    "description": 'Generate new curves on points by interpolating between existing curves',
    "inputs": [
        {"name": 'Guide Curves', "identifier": 'Guide Curves', "type": 'GEOMETRY'},
        {"name": 'Guide Up', "identifier": 'Guide Up', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Guide Group ID', "identifier": 'Guide Group ID', "type": 'INT', "default_value": 0},
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Point Up', "identifier": 'Point Up', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Point Group ID', "identifier": 'Point Group ID', "type": 'INT', "default_value": 0},
        {"name": 'Max Neighbors', "identifier": 'Max Neighbors', "type": 'INT', "default_value": 4}
    ],
    "outputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'},
        {"name": 'Closest Index', "identifier": 'Closest Index', "type": 'INT'},
        {"name": 'Closest Weight', "identifier": 'Closest Weight', "type": 'VALUE'}
    ],
},
    'GeometryNodeOffsetPointInCurve': {
    "name": 'Offset Point in Curve',
    "type": 'GeometryNodeOffsetPointInCurve',
    "category": 'Curve',
    "description": 'Offset a control point index within its curve',
    "inputs": [
        {"name": 'Point Index', "identifier": 'Point Index', "type": 'INT', "default_value": 0},
        {"name": 'Offset', "identifier": 'Offset', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Is Valid Offset', "identifier": 'Is Valid Offset', "type": 'BOOLEAN'},
        {"name": 'Point Index', "identifier": 'Point Index', "type": 'INT'}
    ],
},
    'GeometryNodePointsOfCurve': {
    "name": 'Points of Curve',
    "type": 'GeometryNodePointsOfCurve',
    "category": 'Curve',
    "description": 'Retrieve a point index within a curve',
    "inputs": [
        {"name": 'Curve Index', "identifier": 'Curve Index', "type": 'INT', "default_value": 0},
        {"name": 'Weights', "identifier": 'Weights', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Sort Index', "identifier": 'Sort Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Point Index', "identifier": 'Point Index', "type": 'INT'},
        {"name": 'Total', "identifier": 'Total', "type": 'INT'}
    ],
},
    'GeometryNodePointsToCurves': {
    "name": 'Points to Curves',
    "type": 'GeometryNodePointsToCurves',
    "category": 'Curve',
    "description": 'Split all points to curve by its group ID and reorder by weight',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Curve Group ID', "identifier": 'Curve Group ID', "type": 'INT', "default_value": 0},
        {"name": 'Weight', "identifier": 'Weight', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeResampleCurve': {
    "name": 'Resample Curve',
    "type": 'GeometryNodeResampleCurve',
    "category": 'Curve',
    "description": 'Generate a poly spline for each input spline',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Count', "identifier": 'Count', "type": 'INT', "default_value": 10},
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE', "default_value": 0.10000000149011612}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeReverseCurve': {
    "name": 'Reverse Curve',
    "type": 'GeometryNodeReverseCurve',
    "category": 'Curve',
    "description": 'Change the direction of curves by swapping their start and end data',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSampleCurve': {
    "name": 'Sample Curve',
    "type": 'GeometryNodeSampleCurve',
    "category": 'Curve',
    "description": 'Retrieve data from a point on a curve at a certain distance from its start',
    "inputs": [
        {"name": 'Curves', "identifier": 'Curves', "type": 'GEOMETRY'},
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Factor', "identifier": 'Factor', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Curve Index', "identifier": 'Curve Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR'},
        {"name": 'Tangent', "identifier": 'Tangent', "type": 'VECTOR'},
        {"name": 'Normal', "identifier": 'Normal', "type": 'VECTOR'}
    ],
},
    'GeometryNodeSetCurveHandlePositions': {
    "name": 'Set Handle Positions',
    "type": 'GeometryNodeSetCurveHandlePositions',
    "category": 'Curve',
    "description": 'Set the positions for the handles of Bézier curves',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Offset', "identifier": 'Offset', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetCurveNormal': {
    "name": 'Set Curve Normal',
    "type": 'GeometryNodeSetCurveNormal',
    "category": 'Curve',
    "description": 'Set the evaluation mode for curve normals',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Normal', "identifier": 'Normal', "type": 'VECTOR', "default_value": [0.0, 0.0, 1.0]}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetCurveRadius': {
    "name": 'Set Curve Radius',
    "type": 'GeometryNodeSetCurveRadius',
    "category": 'Curve',
    "description": 'Set the radius of the curve at each control point',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.004999999888241291}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetCurveTilt': {
    "name": 'Set Curve Tilt',
    "type": 'GeometryNodeSetCurveTilt',
    "category": 'Curve',
    "description": 'Set the tilt angle at each curve control point',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Tilt', "identifier": 'Tilt', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeStringToCurves': {
    "name": 'String to Curves',
    "type": 'GeometryNodeStringToCurves',
    "category": 'Curve',
    "description": 'Generate a paragraph of text with a specific font, using a curve instance to store each character',
    "inputs": [
        {"name": 'String', "identifier": 'String', "type": 'STRING', "default_value": ''},
        {"name": 'Size', "identifier": 'Size', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Character Spacing', "identifier": 'Character Spacing', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Word Spacing', "identifier": 'Word Spacing', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Line Spacing', "identifier": 'Line Spacing', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Text Box Width', "identifier": 'Text Box Width', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Text Box Height', "identifier": 'Text Box Height', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Curve Instances', "identifier": 'Curve Instances', "type": 'GEOMETRY'},
        {"name": 'Remainder', "identifier": 'Remainder', "type": 'STRING'},
        {"name": 'Line', "identifier": 'Line', "type": 'INT'},
        {"name": 'Pivot Point', "identifier": 'Pivot Point', "type": 'VECTOR'}
    ],
},
    'GeometryNodeSubdivideCurve': {
    "name": 'Subdivide Curve',
    "type": 'GeometryNodeSubdivideCurve',
    "category": 'Curve',
    "description": 'Dividing each curve segment into a specified number of pieces',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Cuts', "identifier": 'Cuts', "type": 'INT', "default_value": 1}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeTrimCurve': {
    "name": 'Trim Curve',
    "type": 'GeometryNodeTrimCurve',
    "category": 'Curve',
    "description": 'Shorten curves by removing portions at the start or end',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Start', "identifier": 'Start', "type": 'VALUE', "default_value": 0.0},
        {"name": 'End', "identifier": 'End', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Start', "identifier": 'Start_001', "type": 'VALUE', "default_value": 0.0},
        {"name": 'End', "identifier": 'End_001', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeClosureInput': {
    "name": 'Closure Input',
    "type": 'GeometryNodeClosureInput',
    "category": 'Input',
    "description": '',
    "inputs": [

    ],
    "outputs": [
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeForeachGeometryElementInput': {
    "name": 'For Each Geometry Element Input',
    "type": 'GeometryNodeForeachGeometryElementInput',
    "category": 'Input',
    "description": '',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Index', "identifier": 'Index', "type": 'INT'},
        {"name": 'Element', "identifier": 'Element', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeInputActiveCamera': {
    "name": 'Active Camera',
    "type": 'GeometryNodeInputActiveCamera',
    "category": 'Input',
    "description": "Retrieve the scene's active camera",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Active Camera', "identifier": 'Active Camera', "type": 'OBJECT'}
    ],
},
    'GeometryNodeInputCollection': {
    "name": 'Collection',
    "type": 'GeometryNodeInputCollection',
    "category": 'Input',
    "description": 'Output a single collection',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Collection', "identifier": 'Collection', "type": 'COLLECTION'}
    ],
},
    'GeometryNodeInputCurveHandlePositions': {
    "name": 'Curve Handle Positions',
    "type": 'GeometryNodeInputCurveHandlePositions',
    "category": 'Input',
    "description": "Retrieve the position of each Bézier control point's handles",
    "inputs": [
        {"name": 'Relative', "identifier": 'Relative', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Left', "identifier": 'Left', "type": 'VECTOR'},
        {"name": 'Right', "identifier": 'Right', "type": 'VECTOR'}
    ],
},
    'GeometryNodeInputCurveTilt': {
    "name": 'Curve Tilt',
    "type": 'GeometryNodeInputCurveTilt',
    "category": 'Input',
    "description": "Retrieve the angle at each control point used to twist the curve's normal around its tangent",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Tilt', "identifier": 'Tilt', "type": 'VALUE'}
    ],
},
    'GeometryNodeInputEdgeSmooth': {
    "name": 'Is Edge Smooth',
    "type": 'GeometryNodeInputEdgeSmooth',
    "category": 'Input',
    "description": 'Retrieve whether each edge is marked for smooth or split normals',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Smooth', "identifier": 'Smooth', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeInputID': {
    "name": 'ID',
    "type": 'GeometryNodeInputID',
    "category": 'Input',
    "description": 'Retrieve a stable random identifier value from the "id" attribute on the point domain, or the index if the attribute does not exist',
    "inputs": [

    ],
    "outputs": [
        {"name": 'ID', "identifier": 'ID', "type": 'INT'}
    ],
},
    'GeometryNodeInputImage': {
    "name": 'Image',
    "type": 'GeometryNodeInputImage',
    "category": 'Input',
    "description": 'Input an image data-block',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Image', "identifier": 'Image', "type": 'IMAGE'}
    ],
},
    'GeometryNodeInputIndex': {
    "name": 'Index',
    "type": 'GeometryNodeInputIndex',
    "category": 'Input',
    "description": 'Retrieve an integer value indicating the position of each element in the list, starting at zero',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Index', "identifier": 'Index', "type": 'INT'}
    ],
},
    'GeometryNodeInputInstanceBounds': {
    "name": 'Instance Bounds',
    "type": 'GeometryNodeInputInstanceBounds',
    "category": 'Input',
    "description": "Calculate position bounds of each instance's geometry set",
    "inputs": [
        {"name": 'Use Radius', "identifier": 'Use Radius', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Min', "identifier": 'Min', "type": 'VECTOR'},
        {"name": 'Max', "identifier": 'Max', "type": 'VECTOR'}
    ],
},
    'GeometryNodeInputInstanceRotation': {
    "name": 'Instance Rotation',
    "type": 'GeometryNodeInputInstanceRotation',
    "category": 'Input',
    "description": 'Retrieve the rotation of each instance in the geometry',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION'}
    ],
},
    'GeometryNodeInputInstanceScale': {
    "name": 'Instance Scale',
    "type": 'GeometryNodeInputInstanceScale',
    "category": 'Input',
    "description": 'Retrieve the scale of each instance in the geometry',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Scale', "identifier": 'Scale', "type": 'VECTOR'}
    ],
},
    'GeometryNodeInputMaterial': {
    "name": 'Material',
    "type": 'GeometryNodeInputMaterial',
    "category": 'Input',
    "description": 'Output a single material',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Material', "identifier": 'Material', "type": 'MATERIAL'}
    ],
},
    'GeometryNodeInputMaterialIndex': {
    "name": 'Material Index',
    "type": 'GeometryNodeInputMaterialIndex',
    "category": 'Input',
    "description": "Retrieve the index of the material used for each element in the geometry's list of materials",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Material Index', "identifier": 'Material Index', "type": 'INT'}
    ],
},
    'GeometryNodeInputMeshEdgeAngle': {
    "name": 'Edge Angle',
    "type": 'GeometryNodeInputMeshEdgeAngle',
    "category": 'Input',
    "description": 'The angle between the normals of connected manifold faces',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Unsigned Angle', "identifier": 'Unsigned Angle', "type": 'VALUE'},
        {"name": 'Signed Angle', "identifier": 'Signed Angle', "type": 'VALUE'}
    ],
},
    'GeometryNodeInputMeshEdgeNeighbors': {
    "name": 'Edge Neighbors',
    "type": 'GeometryNodeInputMeshEdgeNeighbors',
    "category": 'Input',
    "description": 'Retrieve the number of faces that use each edge as one of their sides',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Face Count', "identifier": 'Face Count', "type": 'INT'}
    ],
},
    'GeometryNodeInputMeshEdgeVertices': {
    "name": 'Edge Vertices',
    "type": 'GeometryNodeInputMeshEdgeVertices',
    "category": 'Input',
    "description": 'Retrieve topology information relating to each edge of a mesh',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Vertex Index 1', "identifier": 'Vertex Index 1', "type": 'INT'},
        {"name": 'Vertex Index 2', "identifier": 'Vertex Index 2', "type": 'INT'},
        {"name": 'Position 1', "identifier": 'Position 1', "type": 'VECTOR'},
        {"name": 'Position 2', "identifier": 'Position 2', "type": 'VECTOR'}
    ],
},
    'GeometryNodeInputMeshFaceArea': {
    "name": 'Face Area',
    "type": 'GeometryNodeInputMeshFaceArea',
    "category": 'Input',
    "description": "Calculate the surface area of a mesh's faces",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Area', "identifier": 'Area', "type": 'VALUE'}
    ],
},
    'GeometryNodeInputMeshFaceIsPlanar': {
    "name": 'Is Face Planar',
    "type": 'GeometryNodeInputMeshFaceIsPlanar',
    "category": 'Input',
    "description": 'Retrieve whether all triangles in a face are on the same plane, i.e. whether they have the same normal',
    "inputs": [
        {"name": 'Threshold', "identifier": 'Threshold', "type": 'VALUE', "default_value": 0.009999999776482582}
    ],
    "outputs": [
        {"name": 'Planar', "identifier": 'Planar', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeInputMeshFaceNeighbors': {
    "name": 'Face Neighbors',
    "type": 'GeometryNodeInputMeshFaceNeighbors',
    "category": 'Input',
    "description": 'Retrieve topology information relating to each face of a mesh',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Vertex Count', "identifier": 'Vertex Count', "type": 'INT'},
        {"name": 'Face Count', "identifier": 'Face Count', "type": 'INT'}
    ],
},
    'GeometryNodeInputMeshIsland': {
    "name": 'Mesh Island',
    "type": 'GeometryNodeInputMeshIsland',
    "category": 'Input',
    "description": 'Retrieve information about separate connected regions in a mesh',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Island Index', "identifier": 'Island Index', "type": 'INT'},
        {"name": 'Island Count', "identifier": 'Island Count', "type": 'INT'}
    ],
},
    'GeometryNodeInputMeshVertexNeighbors': {
    "name": 'Vertex Neighbors',
    "type": 'GeometryNodeInputMeshVertexNeighbors',
    "category": 'Input',
    "description": 'Retrieve topology information relating to each vertex of a mesh',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Vertex Count', "identifier": 'Vertex Count', "type": 'INT'},
        {"name": 'Face Count', "identifier": 'Face Count', "type": 'INT'}
    ],
},
    'GeometryNodeInputNamedAttribute': {
    "name": 'Named Attribute',
    "type": 'GeometryNodeInputNamedAttribute',
    "category": 'Input',
    "description": 'Retrieve the data of a specified attribute',
    "inputs": [
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Attribute', "identifier": 'Attribute', "type": 'VALUE'},
        {"name": 'Exists', "identifier": 'Exists', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeInputNamedLayerSelection': {
    "name": 'Named Layer Selection',
    "type": 'GeometryNodeInputNamedLayerSelection',
    "category": 'Input',
    "description": 'Output a selection of a Grease Pencil layer',
    "inputs": [
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeInputNormal': {
    "name": 'Normal',
    "type": 'GeometryNodeInputNormal',
    "category": 'Input',
    "description": 'Retrieve a unit length vector indicating the direction pointing away from the geometry at each element',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Normal', "identifier": 'Normal', "type": 'VECTOR'},
        {"name": 'True Normal', "identifier": 'True Normal', "type": 'VECTOR'}
    ],
},
    'GeometryNodeInputObject': {
    "name": 'Object',
    "type": 'GeometryNodeInputObject',
    "category": 'Input',
    "description": 'Output a single object',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Object', "identifier": 'Object', "type": 'OBJECT'}
    ],
},
    'GeometryNodeInputPosition': {
    "name": 'Position',
    "type": 'GeometryNodeInputPosition',
    "category": 'Input',
    "description": 'Retrieve a vector indicating the location of each element',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR'}
    ],
},
    'GeometryNodeInputRadius': {
    "name": 'Radius',
    "type": 'GeometryNodeInputRadius',
    "category": 'Input',
    "description": 'Retrieve the radius at each point on curve or point cloud geometry',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE'}
    ],
},
    'GeometryNodeInputSceneTime': {
    "name": 'Scene Time',
    "type": 'GeometryNodeInputSceneTime',
    "category": 'Input',
    "description": "Retrieve the current time in the scene's animation in units of seconds or frames",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Seconds', "identifier": 'Seconds', "type": 'VALUE'},
        {"name": 'Frame', "identifier": 'Frame', "type": 'VALUE'}
    ],
},
    'GeometryNodeInputShadeSmooth': {
    "name": 'Is Face Smooth',
    "type": 'GeometryNodeInputShadeSmooth',
    "category": 'Input',
    "description": 'Retrieve whether each face is marked for smooth or sharp normals',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Smooth', "identifier": 'Smooth', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeInputShortestEdgePaths': {
    "name": 'Shortest Edge Paths',
    "type": 'GeometryNodeInputShortestEdgePaths',
    "category": 'Input',
    "description": 'Find the shortest paths along mesh edges to selected end vertices, with customizable cost per edge',
    "inputs": [
        {"name": 'End Vertex', "identifier": 'End Vertex', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Edge Cost', "identifier": 'Edge Cost', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Next Vertex Index', "identifier": 'Next Vertex Index', "type": 'INT'},
        {"name": 'Total Cost', "identifier": 'Total Cost', "type": 'VALUE'}
    ],
},
    'GeometryNodeInputSplineCyclic': {
    "name": 'Is Spline Cyclic',
    "type": 'GeometryNodeInputSplineCyclic',
    "category": 'Input',
    "description": 'Retrieve whether each spline endpoint connects to the beginning',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Cyclic', "identifier": 'Cyclic', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeInputSplineResolution': {
    "name": 'Spline Resolution',
    "type": 'GeometryNodeInputSplineResolution',
    "category": 'Input',
    "description": 'Retrieve the number of evaluated points that will be generated for every control point on curves',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT'}
    ],
},
    'GeometryNodeInputTangent': {
    "name": 'Curve Tangent',
    "type": 'GeometryNodeInputTangent',
    "category": 'Input',
    "description": 'Retrieve the direction of curves at each control point',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Tangent', "identifier": 'Tangent', "type": 'VECTOR'}
    ],
},
    'GeometryNodeRepeatInput': {
    "name": 'Repeat Input',
    "type": 'GeometryNodeRepeatInput',
    "category": 'Input',
    "description": '',
    "inputs": [
        {"name": 'Iterations', "identifier": 'Iterations', "type": 'INT', "default_value": 1},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Iteration', "identifier": 'Iteration', "type": 'INT'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeSimulationInput': {
    "name": 'Simulation Input',
    "type": 'GeometryNodeSimulationInput',
    "category": 'Input',
    "description": 'Input data for the simulation zone',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Delta Time', "identifier": 'Delta Time', "type": 'VALUE'}
    ],
},
    'GeometryNodeGeometryToInstance': {
    "name": 'Geometry to Instance',
    "type": 'GeometryNodeGeometryToInstance',
    "category": 'Instances',
    "description": 'Convert each input geometry into an instance, which can be much faster than the Join Geometry node when the inputs are large',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeInstanceOnPoints': {
    "name": 'Instance on Points',
    "type": 'GeometryNodeInstanceOnPoints',
    "category": 'Instances',
    "description": 'Generate a reference to geometry at each of the input points, without duplicating its underlying data',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Instance', "identifier": 'Instance', "type": 'GEOMETRY'},
        {"name": 'Pick Instance', "identifier": 'Pick Instance', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Instance Index', "identifier": 'Instance Index', "type": 'INT', "default_value": 0},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Scale', "identifier": 'Scale', "type": 'VECTOR', "default_value": [1.0, 1.0, 1.0]}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeInstanceTransform': {
    "name": 'Instance Transform',
    "type": 'GeometryNodeInstanceTransform',
    "category": 'Instances',
    "description": 'Retrieve the full transformation of each instance in the geometry',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Transform', "identifier": 'Transform', "type": 'MATRIX'}
    ],
},
    'GeometryNodeInstancesToPoints': {
    "name": 'Instances to Points',
    "type": 'GeometryNodeInstancesToPoints',
    "category": 'Instances',
    "description": 'Generate points at the origins of instances.\nNote: Nested instances are not affected by this node',
    "inputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.05000000074505806}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeRealizeInstances': {
    "name": 'Realize Instances',
    "type": 'GeometryNodeRealizeInstances',
    "category": 'Instances',
    "description": 'Convert instances into real geometry data',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Realize All', "identifier": 'Realize All', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Depth', "identifier": 'Depth', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeRotateInstances': {
    "name": 'Rotate Instances',
    "type": 'GeometryNodeRotateInstances',
    "category": 'Instances',
    "description": 'Rotate geometry instances in local or global space',
    "inputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Pivot Point', "identifier": 'Pivot Point', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Local Space', "identifier": 'Local Space', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeScaleInstances': {
    "name": 'Scale Instances',
    "type": 'GeometryNodeScaleInstances',
    "category": 'Instances',
    "description": 'Scale geometry instances in local or global space',
    "inputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Scale', "identifier": 'Scale', "type": 'VECTOR', "default_value": [1.0, 1.0, 1.0]},
        {"name": 'Center', "identifier": 'Center', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Local Space', "identifier": 'Local Space', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetInstanceTransform': {
    "name": 'Set Instance Transform',
    "type": 'GeometryNodeSetInstanceTransform',
    "category": 'Instances',
    "description": 'Set the transformation matrix of every instance',
    "inputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Transform', "identifier": 'Transform', "type": 'MATRIX'}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSplitToInstances': {
    "name": 'Split to Instances',
    "type": 'GeometryNodeSplitToInstances',
    "category": 'Instances',
    "description": 'Create separate geometries containing the elements from the same group',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT'}
    ],
},
    'GeometryNodeTranslateInstances': {
    "name": 'Translate Instances',
    "type": 'GeometryNodeTranslateInstances',
    "category": 'Instances',
    "description": 'Move top-level geometry instances in local or global space',
    "inputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Translation', "identifier": 'Translation', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Local Space', "identifier": 'Local Space', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMaterialSelection': {
    "name": 'Material Selection',
    "type": 'GeometryNodeMaterialSelection',
    "category": 'Material',
    "description": 'Provide a selection of faces that use the specified material',
    "inputs": [
        {"name": 'Material', "identifier": 'Material', "type": 'MATERIAL', "default_value": None}
    ],
    "outputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeReplaceMaterial': {
    "name": 'Replace Material',
    "type": 'GeometryNodeReplaceMaterial',
    "category": 'Material',
    "description": 'Swap one material with another',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Old', "identifier": 'Old', "type": 'MATERIAL', "default_value": None},
        {"name": 'New', "identifier": 'New', "type": 'MATERIAL', "default_value": None}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetMaterial': {
    "name": 'Set Material',
    "type": 'GeometryNodeSetMaterial',
    "category": 'Material',
    "description": 'Assign a material to geometry elements',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Material', "identifier": 'Material', "type": 'MATERIAL', "default_value": None}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetMaterialIndex': {
    "name": 'Set Material Index',
    "type": 'GeometryNodeSetMaterialIndex',
    "category": 'Material',
    "description": 'Set the material index for each selected geometry element',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Material Index', "identifier": 'Material Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCurveToMesh': {
    "name": 'Curve to Mesh',
    "type": 'GeometryNodeCurveToMesh',
    "category": 'Mesh',
    "description": 'Convert curves into a mesh, optionally with a custom profile shape defined by curves',
    "inputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Profile Curve', "identifier": 'Profile Curve', "type": 'GEOMETRY'},
        {"name": 'Scale', "identifier": 'Scale', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Fill Caps', "identifier": 'Fill Caps', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeDualMesh': {
    "name": 'Dual Mesh',
    "type": 'GeometryNodeDualMesh',
    "category": 'Mesh',
    "description": 'Convert Faces into vertices and vertices into faces',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Keep Boundaries', "identifier": 'Keep Boundaries', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Dual Mesh', "identifier": 'Dual Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeExtrudeMesh': {
    "name": 'Extrude Mesh',
    "type": 'GeometryNodeExtrudeMesh',
    "category": 'Mesh',
    "description": 'Generate new vertices, edges, or faces from selected elements and move them based on an offset while keeping them connected by their boundary',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Offset', "identifier": 'Offset', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Offset Scale', "identifier": 'Offset Scale', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Individual', "identifier": 'Individual', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Top', "identifier": 'Top', "type": 'BOOLEAN'},
        {"name": 'Side', "identifier": 'Side', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeGridToMesh': {
    "name": 'Grid to Mesh',
    "type": 'GeometryNodeGridToMesh',
    "category": 'Mesh',
    "description": 'Generate a mesh on the "surface" of a volume grid',
    "inputs": [
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Threshold', "identifier": 'Threshold', "type": 'VALUE', "default_value": 0.10000000149011612},
        {"name": 'Adaptivity', "identifier": 'Adaptivity', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMeshBoolean': {
    "name": 'Mesh Boolean',
    "type": 'GeometryNodeMeshBoolean',
    "category": 'Mesh',
    "description": 'Cut, subtract, or join multiple mesh inputs',
    "inputs": [
        {"name": 'Mesh 1', "identifier": 'Mesh 1', "type": 'GEOMETRY'},
        {"name": 'Mesh 2', "identifier": 'Mesh 2', "type": 'GEOMETRY'},
        {"name": 'Self Intersection', "identifier": 'Self Intersection', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Hole Tolerant', "identifier": 'Hole Tolerant', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Intersecting Edges', "identifier": 'Intersecting Edges', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeMeshCircle': {
    "name": 'Mesh Circle',
    "type": 'GeometryNodeMeshCircle',
    "category": 'Mesh',
    "description": 'Generate a circular ring of edges',
    "inputs": [
        {"name": 'Vertices', "identifier": 'Vertices', "type": 'INT', "default_value": 32},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMeshCone': {
    "name": 'Cone',
    "type": 'GeometryNodeMeshCone',
    "category": 'Mesh',
    "description": 'Generate a cone mesh',
    "inputs": [
        {"name": 'Vertices', "identifier": 'Vertices', "type": 'INT', "default_value": 32},
        {"name": 'Side Segments', "identifier": 'Side Segments', "type": 'INT', "default_value": 1},
        {"name": 'Fill Segments', "identifier": 'Fill Segments', "type": 'INT', "default_value": 1},
        {"name": 'Radius Top', "identifier": 'Radius Top', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Radius Bottom', "identifier": 'Radius Bottom', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Depth', "identifier": 'Depth', "type": 'VALUE', "default_value": 2.0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Top', "identifier": 'Top', "type": 'BOOLEAN'},
        {"name": 'Bottom', "identifier": 'Bottom', "type": 'BOOLEAN'},
        {"name": 'Side', "identifier": 'Side', "type": 'BOOLEAN'},
        {"name": 'UV Map', "identifier": 'UV Map', "type": 'VECTOR'}
    ],
},
    'GeometryNodeMeshCube': {
    "name": 'Cube',
    "type": 'GeometryNodeMeshCube',
    "category": 'Mesh',
    "description": 'Generate a cuboid mesh with variable side lengths and subdivisions',
    "inputs": [
        {"name": 'Size', "identifier": 'Size', "type": 'VECTOR', "default_value": [1.0, 1.0, 1.0]},
        {"name": 'Vertices X', "identifier": 'Vertices X', "type": 'INT', "default_value": 2},
        {"name": 'Vertices Y', "identifier": 'Vertices Y', "type": 'INT', "default_value": 2},
        {"name": 'Vertices Z', "identifier": 'Vertices Z', "type": 'INT', "default_value": 2}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'UV Map', "identifier": 'UV Map', "type": 'VECTOR'}
    ],
},
    'GeometryNodeMeshCylinder': {
    "name": 'Cylinder',
    "type": 'GeometryNodeMeshCylinder',
    "category": 'Mesh',
    "description": 'Generate a cylinder mesh',
    "inputs": [
        {"name": 'Vertices', "identifier": 'Vertices', "type": 'INT', "default_value": 32},
        {"name": 'Side Segments', "identifier": 'Side Segments', "type": 'INT', "default_value": 1},
        {"name": 'Fill Segments', "identifier": 'Fill Segments', "type": 'INT', "default_value": 1},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Depth', "identifier": 'Depth', "type": 'VALUE', "default_value": 2.0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Top', "identifier": 'Top', "type": 'BOOLEAN'},
        {"name": 'Side', "identifier": 'Side', "type": 'BOOLEAN'},
        {"name": 'Bottom', "identifier": 'Bottom', "type": 'BOOLEAN'},
        {"name": 'UV Map', "identifier": 'UV Map', "type": 'VECTOR'}
    ],
},
    'GeometryNodeMeshFaceSetBoundaries': {
    "name": 'Face Group Boundaries',
    "type": 'GeometryNodeMeshFaceSetBoundaries',
    "category": 'Mesh',
    "description": 'Find edges on the boundaries between groups of faces with the same ID value',
    "inputs": [
        {"name": 'Face Group ID', "identifier": 'Face Set', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Boundary Edges', "identifier": 'Boundary Edges', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeMeshGrid': {
    "name": 'Grid',
    "type": 'GeometryNodeMeshGrid',
    "category": 'Mesh',
    "description": 'Generate a planar mesh on the XY plane',
    "inputs": [
        {"name": 'Size X', "identifier": 'Size X', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Size Y', "identifier": 'Size Y', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Vertices X', "identifier": 'Vertices X', "type": 'INT', "default_value": 3},
        {"name": 'Vertices Y', "identifier": 'Vertices Y', "type": 'INT', "default_value": 3}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'UV Map', "identifier": 'UV Map', "type": 'VECTOR'}
    ],
},
    'GeometryNodeMeshIcoSphere': {
    "name": 'Ico Sphere',
    "type": 'GeometryNodeMeshIcoSphere',
    "category": 'Mesh',
    "description": 'Generate a spherical mesh that consists of equally sized triangles',
    "inputs": [
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Subdivisions', "identifier": 'Subdivisions', "type": 'INT', "default_value": 1}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'UV Map', "identifier": 'UV Map', "type": 'VECTOR'}
    ],
},
    'GeometryNodeMeshLine': {
    "name": 'Mesh Line',
    "type": 'GeometryNodeMeshLine',
    "category": 'Mesh',
    "description": 'Generate vertices in a line and connect them with edges',
    "inputs": [
        {"name": 'Count', "identifier": 'Count', "type": 'INT', "default_value": 10},
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Start Location', "identifier": 'Start Location', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Offset', "identifier": 'Offset', "type": 'VECTOR', "default_value": [0.0, 0.0, 1.0]}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMeshToCurve': {
    "name": 'Mesh to Curve',
    "type": 'GeometryNodeMeshToCurve',
    "category": 'Mesh',
    "description": 'Generate a curve from a mesh',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMeshToDensityGrid': {
    "name": 'Mesh to Density Grid',
    "type": 'GeometryNodeMeshToDensityGrid',
    "category": 'Mesh',
    "description": 'Create a filled volume grid from a mesh',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Voxel Size', "identifier": 'Voxel Size', "type": 'VALUE', "default_value": 0.30000001192092896},
        {"name": 'Gradient Width', "identifier": 'Gradient Width', "type": 'VALUE', "default_value": 0.20000000298023224}
    ],
    "outputs": [
        {"name": 'Density Grid', "identifier": 'Density Grid', "type": 'VALUE'}
    ],
},
    'GeometryNodeMeshToPoints': {
    "name": 'Mesh to Points',
    "type": 'GeometryNodeMeshToPoints',
    "category": 'Mesh',
    "description": "Generate a point cloud from a mesh's vertices",
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.05000000074505806}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMeshToSDFGrid': {
    "name": 'Mesh to SDF Grid',
    "type": 'GeometryNodeMeshToSDFGrid',
    "category": 'Mesh',
    "description": 'Create a signed distance volume grid from a mesh',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Voxel Size', "identifier": 'Voxel Size', "type": 'VALUE', "default_value": 0.30000001192092896},
        {"name": 'Band Width', "identifier": 'Band Width', "type": 'INT', "default_value": 3}
    ],
    "outputs": [
        {"name": 'SDF Grid', "identifier": 'SDF Grid', "type": 'VALUE'}
    ],
},
    'GeometryNodeMeshToVolume': {
    "name": 'Mesh to Volume',
    "type": 'GeometryNodeMeshToVolume',
    "category": 'Mesh',
    "description": "Create a fog volume with the shape of the input mesh's surface",
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Voxel Size', "identifier": 'Voxel Size', "type": 'VALUE', "default_value": 0.30000001192092896},
        {"name": 'Voxel Amount', "identifier": 'Voxel Amount', "type": 'VALUE', "default_value": 64.0},
        {"name": 'Interior Band Width', "identifier": 'Interior Band Width', "type": 'VALUE', "default_value": 0.20000000298023224}
    ],
    "outputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMeshUVSphere': {
    "name": 'UV Sphere',
    "type": 'GeometryNodeMeshUVSphere',
    "category": 'Mesh',
    "description": 'Generate a spherical mesh with quads, except for triangles at the top and bottom',
    "inputs": [
        {"name": 'Segments', "identifier": 'Segments', "type": 'INT', "default_value": 32},
        {"name": 'Rings', "identifier": 'Rings', "type": 'INT', "default_value": 16},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'UV Map', "identifier": 'UV Map', "type": 'VECTOR'}
    ],
},
    'GeometryNodeSetMeshNormal': {
    "name": 'Set Mesh Normal',
    "type": 'GeometryNodeSetMeshNormal',
    "category": 'Mesh',
    "description": 'Store a normal vector for each mesh element',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Remove Custom', "identifier": 'Remove Custom', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Edge Sharpness', "identifier": 'Edge Sharpness', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Face Sharpness', "identifier": 'Face Sharpness', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSubdivideMesh': {
    "name": 'Subdivide Mesh',
    "type": 'GeometryNodeSubdivideMesh',
    "category": 'Mesh',
    "description": 'Divide mesh faces into smaller ones without changing the shape or volume, using linear interpolation to place the new vertices',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Level', "identifier": 'Level', "type": 'INT', "default_value": 1}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeVolumeToMesh': {
    "name": 'Volume to Mesh',
    "type": 'GeometryNodeVolumeToMesh',
    "category": 'Mesh',
    "description": 'Generate a mesh on the "surface" of a volume',
    "inputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'},
        {"name": 'Voxel Size', "identifier": 'Voxel Size', "type": 'VALUE', "default_value": 0.30000001192092896},
        {"name": 'Voxel Amount', "identifier": 'Voxel Amount', "type": 'VALUE', "default_value": 64.0},
        {"name": 'Threshold', "identifier": 'Threshold', "type": 'VALUE', "default_value": 0.10000000149011612},
        {"name": 'Adaptivity', "identifier": 'Adaptivity', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNode': {
    "name": 'Geometry Node',
    "type": 'GeometryNode',
    "category": 'Other',
    "description": '',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeAccumulateField': {
    "name": 'Accumulate Field',
    "type": 'GeometryNodeAccumulateField',
    "category": 'Other',
    "description": 'Add the values of an evaluated field together and output the running total for each element',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Group ID', "identifier": 'Group Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Leading', "identifier": 'Leading', "type": 'VALUE'},
        {"name": 'Trailing', "identifier": 'Trailing', "type": 'VALUE'},
        {"name": 'Total', "identifier": 'Total', "type": 'VALUE'}
    ],
},
    'GeometryNodeBake': {
    "name": 'Bake',
    "type": 'GeometryNodeBake',
    "category": 'Other',
    "description": 'Cache the incoming data so that it can be used without recomputation',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeBoundBox': {
    "name": 'Bounding Box',
    "type": 'GeometryNodeBoundBox',
    "category": 'Other',
    "description": "Calculate the limits of a geometry's positions and generate a box mesh with those dimensions",
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Use Radius', "identifier": 'Use Radius', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Bounding Box', "identifier": 'Bounding Box', "type": 'GEOMETRY'},
        {"name": 'Min', "identifier": 'Min', "type": 'VECTOR'},
        {"name": 'Max', "identifier": 'Max', "type": 'VECTOR'}
    ],
},
    'GeometryNodeCameraInfo': {
    "name": 'Camera Info',
    "type": 'GeometryNodeCameraInfo',
    "category": 'Other',
    "description": 'Retrieve information from a camera object',
    "inputs": [
        {"name": 'Camera', "identifier": 'Camera', "type": 'OBJECT', "default_value": None}
    ],
    "outputs": [
        {"name": 'Projection Matrix', "identifier": 'Projection Matrix', "type": 'MATRIX'},
        {"name": 'Focal Length', "identifier": 'Focal Length', "type": 'VALUE'},
        {"name": 'Sensor', "identifier": 'Sensor', "type": 'VECTOR'},
        {"name": 'Shift', "identifier": 'Shift', "type": 'VECTOR'},
        {"name": 'Clip Start', "identifier": 'Clip Start', "type": 'VALUE'},
        {"name": 'Clip End', "identifier": 'Clip End', "type": 'VALUE'},
        {"name": 'Focus Distance', "identifier": 'Focus Distance', "type": 'VALUE'},
        {"name": 'Is Orthographic', "identifier": 'Is Orthographic', "type": 'BOOLEAN'},
        {"name": 'Orthographic Scale', "identifier": 'Orthographic Scale', "type": 'VALUE'}
    ],
},
    'GeometryNodeCollectionInfo': {
    "name": 'Collection Info',
    "type": 'GeometryNodeCollectionInfo',
    "category": 'Other',
    "description": 'Retrieve geometry instances from a collection',
    "inputs": [
        {"name": 'Collection', "identifier": 'Collection', "type": 'COLLECTION', "default_value": None},
        {"name": 'Separate Children', "identifier": 'Separate Children', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Reset Children', "identifier": 'Reset Children', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCombineBundle': {
    "name": 'Combine Bundle',
    "type": 'GeometryNodeCombineBundle',
    "category": 'Other',
    "description": 'Combine multiple socket values into one.',
    "inputs": [
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Bundle', "identifier": 'Bundle', "type": 'BUNDLE'}
    ],
},
    'GeometryNodeConvexHull': {
    "name": 'Convex Hull',
    "type": 'GeometryNodeConvexHull',
    "category": 'Other',
    "description": 'Create a mesh that encloses all points in the input geometry with the smallest number of points',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Convex Hull', "identifier": 'Convex Hull', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeCornersOfEdge': {
    "name": 'Corners of Edge',
    "type": 'GeometryNodeCornersOfEdge',
    "category": 'Other',
    "description": 'Retrieve face corners connected to edges',
    "inputs": [
        {"name": 'Edge Index', "identifier": 'Edge Index', "type": 'INT', "default_value": 0},
        {"name": 'Weights', "identifier": 'Weights', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Sort Index', "identifier": 'Sort Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT'},
        {"name": 'Total', "identifier": 'Total', "type": 'INT'}
    ],
},
    'GeometryNodeCornersOfFace': {
    "name": 'Corners of Face',
    "type": 'GeometryNodeCornersOfFace',
    "category": 'Other',
    "description": 'Retrieve corners that make up a face',
    "inputs": [
        {"name": 'Face Index', "identifier": 'Face Index', "type": 'INT', "default_value": 0},
        {"name": 'Weights', "identifier": 'Weights', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Sort Index', "identifier": 'Sort Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT'},
        {"name": 'Total', "identifier": 'Total', "type": 'INT'}
    ],
},
    'GeometryNodeCornersOfVertex': {
    "name": 'Corners of Vertex',
    "type": 'GeometryNodeCornersOfVertex',
    "category": 'Other',
    "description": 'Retrieve face corners connected to vertices',
    "inputs": [
        {"name": 'Vertex Index', "identifier": 'Vertex Index', "type": 'INT', "default_value": 0},
        {"name": 'Weights', "identifier": 'Weights', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Sort Index', "identifier": 'Sort Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT'},
        {"name": 'Total', "identifier": 'Total', "type": 'INT'}
    ],
},
    'GeometryNodeCustomGroup': {
    "name": 'Geometry Custom Group',
    "type": 'GeometryNodeCustomGroup',
    "category": 'Other',
    "description": 'Custom Geometry Group Node for Python nodes',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeDeleteGeometry': {
    "name": 'Delete Geometry',
    "type": 'GeometryNodeDeleteGeometry',
    "category": 'Other',
    "description": 'Remove selected elements of a geometry',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeDistributePointsInGrid': {
    "name": 'Distribute Points in Grid',
    "type": 'GeometryNodeDistributePointsInGrid',
    "category": 'Other',
    "description": 'Generate points inside a volume grid',
    "inputs": [
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Seed', "identifier": 'Seed', "type": 'INT', "default_value": 0},
        {"name": 'Spacing', "identifier": 'Spacing', "type": 'VECTOR', "default_value": [0.30000001192092896, 0.30000001192092896, 0.30000001192092896]},
        {"name": 'Threshold', "identifier": 'Threshold', "type": 'VALUE', "default_value": 0.10000000149011612}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeDistributePointsOnFaces': {
    "name": 'Distribute Points on Faces',
    "type": 'GeometryNodeDistributePointsOnFaces',
    "category": 'Other',
    "description": 'Generate points spread out on the surface of a mesh',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Distance Min', "identifier": 'Distance Min', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Density Max', "identifier": 'Density Max', "type": 'VALUE', "default_value": 10.0},
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 10.0},
        {"name": 'Density Factor', "identifier": 'Density Factor', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Seed', "identifier": 'Seed', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Normal', "identifier": 'Normal', "type": 'VECTOR'},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION'}
    ],
},
    'GeometryNodeDuplicateElements': {
    "name": 'Duplicate Elements',
    "type": 'GeometryNodeDuplicateElements',
    "category": 'Other',
    "description": 'Generate an arbitrary number copies of each selected input element',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Amount', "identifier": 'Amount', "type": 'INT', "default_value": 1}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Duplicate Index', "identifier": 'Duplicate Index', "type": 'INT'}
    ],
},
    'GeometryNodeEdgePathsToSelection': {
    "name": 'Edge Paths to Selection',
    "type": 'GeometryNodeEdgePathsToSelection',
    "category": 'Other',
    "description": 'Output a selection of edges by following paths across mesh edges',
    "inputs": [
        {"name": 'Start Vertices', "identifier": 'Start Vertices', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Next Vertex Index', "identifier": 'Next Vertex Index', "type": 'INT', "default_value": -1}
    ],
    "outputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeEdgesOfCorner': {
    "name": 'Edges of Corner',
    "type": 'GeometryNodeEdgesOfCorner',
    "category": 'Other',
    "description": 'Retrieve the edges on both sides of a face corner',
    "inputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Next Edge Index', "identifier": 'Next Edge Index', "type": 'INT'},
        {"name": 'Previous Edge Index', "identifier": 'Previous Edge Index', "type": 'INT'}
    ],
},
    'GeometryNodeEdgesOfVertex': {
    "name": 'Edges of Vertex',
    "type": 'GeometryNodeEdgesOfVertex',
    "category": 'Other',
    "description": 'Retrieve the edges connected to each vertex',
    "inputs": [
        {"name": 'Vertex Index', "identifier": 'Vertex Index', "type": 'INT', "default_value": 0},
        {"name": 'Weights', "identifier": 'Weights', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Sort Index', "identifier": 'Sort Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Edge Index', "identifier": 'Edge Index', "type": 'INT'},
        {"name": 'Total', "identifier": 'Total', "type": 'INT'}
    ],
},
    'GeometryNodeEdgesToFaceGroups': {
    "name": 'Edges to Face Groups',
    "type": 'GeometryNodeEdgesToFaceGroups',
    "category": 'Other',
    "description": 'Group faces into regions surrounded by the selected boundary edges',
    "inputs": [
        {"name": 'Boundary Edges', "identifier": 'Boundary Edges', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Face Group ID', "identifier": 'Face Group ID', "type": 'INT'}
    ],
},
    'GeometryNodeEvaluateClosure': {
    "name": 'Evaluate Closure',
    "type": 'GeometryNodeEvaluateClosure',
    "category": 'Other',
    "description": '',
    "inputs": [
        {"name": 'Closure', "identifier": 'Closure', "type": 'CLOSURE'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeFaceOfCorner': {
    "name": 'Face of Corner',
    "type": 'GeometryNodeFaceOfCorner',
    "category": 'Other',
    "description": 'Retrieve the face each face corner is part of',
    "inputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Face Index', "identifier": 'Face Index', "type": 'INT'},
        {"name": 'Index in Face', "identifier": 'Index in Face', "type": 'INT'}
    ],
},
    'GeometryNodeFieldAtIndex': {
    "name": 'Evaluate at Index',
    "type": 'GeometryNodeFieldAtIndex',
    "category": 'Other',
    "description": "Retrieve data of other elements in the context's geometry",
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Index', "identifier": 'Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeFieldAverage': {
    "name": 'Field Average',
    "type": 'GeometryNodeFieldAverage',
    "category": 'Other',
    "description": 'Calculate the mean and median of a given field',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Group ID', "identifier": 'Group Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Mean', "identifier": 'Mean', "type": 'VALUE'},
        {"name": 'Median', "identifier": 'Median', "type": 'VALUE'}
    ],
},
    'GeometryNodeFieldMinAndMax': {
    "name": 'Field Min & Max',
    "type": 'GeometryNodeFieldMinAndMax',
    "category": 'Other',
    "description": 'Calculate the minimum and maximum of a given field',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Group ID', "identifier": 'Group Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Min', "identifier": 'Min', "type": 'VALUE'},
        {"name": 'Max', "identifier": 'Max', "type": 'VALUE'}
    ],
},
    'GeometryNodeFieldOnDomain': {
    "name": 'Evaluate on Domain',
    "type": 'GeometryNodeFieldOnDomain',
    "category": 'Other',
    "description": 'Retrieve values from a field on a different domain besides the domain from the context',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeFieldVariance': {
    "name": 'Field Variance',
    "type": 'GeometryNodeFieldVariance',
    "category": 'Other',
    "description": 'Calculate the standard deviation and variance of a given field',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Group ID', "identifier": 'Group Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Standard Deviation', "identifier": 'Standard Deviation', "type": 'VALUE'},
        {"name": 'Variance', "identifier": 'Variance', "type": 'VALUE'}
    ],
},
    'GeometryNodeFlipFaces': {
    "name": 'Flip Faces',
    "type": 'GeometryNodeFlipFaces',
    "category": 'Other',
    "description": 'Reverse the order of the vertices and edges of selected faces, flipping their normal direction',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeGetNamedGrid': {
    "name": 'Get Named Grid',
    "type": 'GeometryNodeGetNamedGrid',
    "category": 'Other',
    "description": 'Get volume grid from a volume geometry with the specified name',
    "inputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'},
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''},
        {"name": 'Remove', "identifier": 'Remove', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'},
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE'}
    ],
},
    'GeometryNodeGizmoDial': {
    "name": 'Dial Gizmo',
    "type": 'GeometryNodeGizmoDial',
    "category": 'Other',
    "description": 'Show a dial gizmo in the viewport for a value',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Up', "identifier": 'Up', "type": 'VECTOR', "default_value": [0.0, 0.0, 1.0]},
        {"name": 'Screen Space', "identifier": 'Screen Space', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 1.0}
    ],
    "outputs": [
        {"name": 'Transform', "identifier": 'Transform', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeGizmoLinear': {
    "name": 'Linear Gizmo',
    "type": 'GeometryNodeGizmoLinear',
    "category": 'Other',
    "description": 'Show a linear gizmo in the viewport for a value',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Direction', "identifier": 'Direction', "type": 'VECTOR', "default_value": [0.0, 0.0, 1.0]}
    ],
    "outputs": [
        {"name": 'Transform', "identifier": 'Transform', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeGridInfo': {
    "name": 'Grid Info',
    "type": 'GeometryNodeGridInfo',
    "category": 'Other',
    "description": 'Retrieve information about a volume grid',
    "inputs": [
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Transform', "identifier": 'Transform', "type": 'MATRIX'},
        {"name": 'Background Value', "identifier": 'Background Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeGroup': {
    "name": 'Group',
    "type": 'GeometryNodeGroup',
    "category": 'Other',
    "description": '',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeImageInfo': {
    "name": 'Image Info',
    "type": 'GeometryNodeImageInfo',
    "category": 'Other',
    "description": 'Retrieve information about an image',
    "inputs": [
        {"name": 'Image', "identifier": 'Image', "type": 'IMAGE', "default_value": None},
        {"name": 'Frame', "identifier": 'Frame', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Width', "identifier": 'Width', "type": 'INT'},
        {"name": 'Height', "identifier": 'Height', "type": 'INT'},
        {"name": 'Has Alpha', "identifier": 'Has Alpha', "type": 'BOOLEAN'},
        {"name": 'Frame Count', "identifier": 'Frame Count', "type": 'INT'},
        {"name": 'FPS', "identifier": 'FPS', "type": 'VALUE'}
    ],
},
    'GeometryNodeImportCSV': {
    "name": 'Import CSV',
    "type": 'GeometryNodeImportCSV',
    "category": 'Other',
    "description": 'Import geometry from an CSV file',
    "inputs": [
        {"name": 'Path', "identifier": 'Path', "type": 'STRING', "default_value": ''},
        {"name": 'Delimiter', "identifier": 'Delimiter', "type": 'STRING', "default_value": ','}
    ],
    "outputs": [
        {"name": 'Point Cloud', "identifier": 'Point Cloud', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeImportOBJ': {
    "name": 'Import OBJ',
    "type": 'GeometryNodeImportOBJ',
    "category": 'Other',
    "description": 'Import geometry from an OBJ file',
    "inputs": [
        {"name": 'Path', "identifier": 'Path', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeImportPLY': {
    "name": 'Import PLY',
    "type": 'GeometryNodeImportPLY',
    "category": 'Other',
    "description": 'Import a point cloud from a PLY file',
    "inputs": [
        {"name": 'Path', "identifier": 'Path', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeImportSTL': {
    "name": 'Import STL',
    "type": 'GeometryNodeImportSTL',
    "category": 'Other',
    "description": 'Import a mesh from an STL file',
    "inputs": [
        {"name": 'Path', "identifier": 'Path', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeImportText': {
    "name": 'Import Text',
    "type": 'GeometryNodeImportText',
    "category": 'Other',
    "description": 'Import a string from a text file',
    "inputs": [
        {"name": 'Path', "identifier": 'Path', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'String', "identifier": 'String', "type": 'STRING'}
    ],
},
    'GeometryNodeImportVDB': {
    "name": 'Import VDB',
    "type": 'GeometryNodeImportVDB',
    "category": 'Other',
    "description": 'Import volume data from a .vdb file',
    "inputs": [
        {"name": 'Path', "identifier": 'Path', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeIndexOfNearest': {
    "name": 'Index of Nearest',
    "type": 'GeometryNodeIndexOfNearest',
    "category": 'Other',
    "description": 'Find the nearest element in a group. Similar to the "Sample Nearest" node',
    "inputs": [
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Index', "identifier": 'Index', "type": 'INT'},
        {"name": 'Has Neighbor', "identifier": 'Has Neighbor', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeIndexSwitch': {
    "name": 'Index Switch',
    "type": 'GeometryNodeIndexSwitch',
    "category": 'Other',
    "description": 'Choose between an arbitrary number of values with an index',
    "inputs": [
        {"name": 'Index', "identifier": 'Index', "type": 'INT', "default_value": 0},
        {"name": '0', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '1', "identifier": 'Item_1', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Output', "identifier": 'Output', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeIsViewport': {
    "name": 'Is Viewport',
    "type": 'GeometryNodeIsViewport',
    "category": 'Other',
    "description": 'Retrieve whether the nodes are being evaluated for the viewport rather than the final render',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Is Viewport', "identifier": 'Is Viewport', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeJoinGeometry': {
    "name": 'Join Geometry',
    "type": 'GeometryNodeJoinGeometry',
    "category": 'Other',
    "description": 'Merge separately generated geometries into a single one',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMenuSwitch': {
    "name": 'Menu Switch',
    "type": 'GeometryNodeMenuSwitch',
    "category": 'Other',
    "description": 'Select from multiple inputs by name',
    "inputs": [
        {"name": 'Menu', "identifier": 'Menu', "type": 'MENU', "default_value": 'A'},
        {"name": 'A', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": 'B', "identifier": 'Item_1', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Output', "identifier": 'Output', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMergeByDistance': {
    "name": 'Merge by Distance',
    "type": 'GeometryNodeMergeByDistance',
    "category": 'Other',
    "description": 'Merge vertices or points within a given distance',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Distance', "identifier": 'Distance', "type": 'VALUE', "default_value": 0.0010000000474974513}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeMergeLayers': {
    "name": 'Merge Layers',
    "type": 'GeometryNodeMergeLayers',
    "category": 'Other',
    "description": 'Join groups of Grease Pencil layers into one',
    "inputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeObjectInfo': {
    "name": 'Object Info',
    "type": 'GeometryNodeObjectInfo',
    "category": 'Other',
    "description": 'Retrieve information from an object',
    "inputs": [
        {"name": 'Object', "identifier": 'Object', "type": 'OBJECT', "default_value": None},
        {"name": 'As Instance', "identifier": 'As Instance', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Transform', "identifier": 'Transform', "type": 'MATRIX'},
        {"name": 'Location', "identifier": 'Location', "type": 'VECTOR'},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION'},
        {"name": 'Scale', "identifier": 'Scale', "type": 'VECTOR'},
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeOffsetCornerInFace': {
    "name": 'Offset Corner in Face',
    "type": 'GeometryNodeOffsetCornerInFace',
    "category": 'Other',
    "description": 'Retrieve corners in the same face as another',
    "inputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT', "default_value": 0},
        {"name": 'Offset', "identifier": 'Offset', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT'}
    ],
},
    'GeometryNodePoints': {
    "name": 'Points',
    "type": 'GeometryNodePoints',
    "category": 'Other',
    "description": 'Generate a point cloud with positions and radii defined by fields',
    "inputs": [
        {"name": 'Count', "identifier": 'Count', "type": 'INT', "default_value": 1},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.10000000149011612}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodePointsToSDFGrid': {
    "name": 'Points to SDF Grid',
    "type": 'GeometryNodePointsToSDFGrid',
    "category": 'Other',
    "description": 'Create a signed distance volume grid from points',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.5},
        {"name": 'Voxel Size', "identifier": 'Voxel Size', "type": 'VALUE', "default_value": 0.30000001192092896}
    ],
    "outputs": [
        {"name": 'SDF Grid', "identifier": 'SDF Grid', "type": 'VALUE'}
    ],
},
    'GeometryNodePointsToVertices': {
    "name": 'Points to Vertices',
    "type": 'GeometryNodePointsToVertices',
    "category": 'Other',
    "description": 'Generate a mesh vertex for each point cloud point',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeProximity': {
    "name": 'Geometry Proximity',
    "type": 'GeometryNodeProximity',
    "category": 'Other',
    "description": 'Compute the closest location on the target geometry',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Target', "type": 'GEOMETRY'},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0},
        {"name": 'Sample Position', "identifier": 'Source Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Sample Group ID', "identifier": 'Sample Group ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR'},
        {"name": 'Distance', "identifier": 'Distance', "type": 'VALUE'},
        {"name": 'Is Valid', "identifier": 'Is Valid', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeRaycast': {
    "name": 'Raycast',
    "type": 'GeometryNodeRaycast',
    "category": 'Other',
    "description": 'Cast rays from the context geometry onto a target geometry, and retrieve information from each hit point',
    "inputs": [
        {"name": 'Target Geometry', "identifier": 'Target Geometry', "type": 'GEOMETRY'},
        {"name": 'Attribute', "identifier": 'Attribute', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Source Position', "identifier": 'Source Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Ray Direction', "identifier": 'Ray Direction', "type": 'VECTOR', "default_value": [0.0, 0.0, -1.0]},
        {"name": 'Ray Length', "identifier": 'Ray Length', "type": 'VALUE', "default_value": 100.0}
    ],
    "outputs": [
        {"name": 'Is Hit', "identifier": 'Is Hit', "type": 'BOOLEAN'},
        {"name": 'Hit Position', "identifier": 'Hit Position', "type": 'VECTOR'},
        {"name": 'Hit Normal', "identifier": 'Hit Normal', "type": 'VECTOR'},
        {"name": 'Hit Distance', "identifier": 'Hit Distance', "type": 'VALUE'},
        {"name": 'Attribute', "identifier": 'Attribute', "type": 'VALUE'}
    ],
},
    'GeometryNodeSDFGridBoolean': {
    "name": 'SDF Grid Boolean',
    "type": 'GeometryNodeSDFGridBoolean',
    "category": 'Other',
    "description": 'Cut, subtract, or join multiple SDF volume grid inputs',
    "inputs": [
        {"name": 'Grid 1', "identifier": 'Grid 1', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Grid 2', "identifier": 'Grid 2', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE'}
    ],
},
    'GeometryNodeSampleGrid': {
    "name": 'Sample Grid',
    "type": 'GeometryNodeSampleGrid',
    "category": 'Other',
    "description": '',
    "inputs": [
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeSampleGridIndex': {
    "name": 'Sample Grid Index',
    "type": 'GeometryNodeSampleGridIndex',
    "category": 'Other',
    "description": 'Retrieve volume grid values at specific voxels',
    "inputs": [
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE', "default_value": 0.0},
        {"name": 'X', "identifier": 'X', "type": 'INT', "default_value": 0},
        {"name": 'Y', "identifier": 'Y', "type": 'INT', "default_value": 0},
        {"name": 'Z', "identifier": 'Z', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeSampleIndex': {
    "name": 'Sample Index',
    "type": 'GeometryNodeSampleIndex',
    "category": 'Other',
    "description": 'Retrieve values from specific geometry elements',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Index', "identifier": 'Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'}
    ],
},
    'GeometryNodeSampleNearest': {
    "name": 'Sample Nearest',
    "type": 'GeometryNodeSampleNearest',
    "category": 'Other',
    "description": 'Find the element of a geometry closest to a position. Similar to the "Index of Nearest" node',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Sample Position', "identifier": 'Sample Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Index', "identifier": 'Index', "type": 'INT'}
    ],
},
    'GeometryNodeSampleNearestSurface': {
    "name": 'Sample Nearest Surface',
    "type": 'GeometryNodeSampleNearestSurface',
    "category": 'Other',
    "description": 'Calculate the interpolated value of a mesh attribute on the closest point of its surface',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0},
        {"name": 'Sample Position', "identifier": 'Sample Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Sample Group ID', "identifier": 'Sample Group ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'},
        {"name": 'Is Valid', "identifier": 'Is Valid', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeSampleUVSurface': {
    "name": 'Sample UV Surface',
    "type": 'GeometryNodeSampleUVSurface',
    "category": 'Other',
    "description": 'Calculate the interpolated values of a mesh attribute at a UV coordinate',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0},
        {"name": 'UV Map', "identifier": 'Source UV Map', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Sample UV', "identifier": 'Sample UV', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE'},
        {"name": 'Is Valid', "identifier": 'Is Valid', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeScaleElements': {
    "name": 'Scale Elements',
    "type": 'GeometryNodeScaleElements',
    "category": 'Other',
    "description": 'Scale groups of connected edges and faces',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Scale', "identifier": 'Scale', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Center', "identifier": 'Center', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Axis', "identifier": 'Axis', "type": 'VECTOR', "default_value": [1.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSelfObject': {
    "name": 'Self Object',
    "type": 'GeometryNodeSelfObject',
    "category": 'Other',
    "description": 'Retrieve the object that contains the geometry nodes modifier currently being executed',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Self Object', "identifier": 'Self Object', "type": 'OBJECT'}
    ],
},
    'GeometryNodeSeparateBundle': {
    "name": 'Separate Bundle',
    "type": 'GeometryNodeSeparateBundle',
    "category": 'Other',
    "description": 'Split a bundle into multiple sockets.',
    "inputs": [
        {"name": 'Bundle', "identifier": 'Bundle', "type": 'BUNDLE'}
    ],
    "outputs": [
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeSeparateComponents': {
    "name": 'Separate Components',
    "type": 'GeometryNodeSeparateComponents',
    "category": 'Other',
    "description": 'Split a geometry into a separate output for each type of data in the geometry',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Curve', "identifier": 'Curve', "type": 'GEOMETRY'},
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'},
        {"name": 'Point Cloud', "identifier": 'Point Cloud', "type": 'GEOMETRY'},
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'},
        {"name": 'Instances', "identifier": 'Instances', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSeparateGeometry': {
    "name": 'Separate Geometry',
    "type": 'GeometryNodeSeparateGeometry',
    "category": 'Other',
    "description": 'Split a geometry into two geometry outputs based on a selection',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'GEOMETRY'},
        {"name": 'Inverted', "identifier": 'Inverted', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetGeometryName': {
    "name": 'Set Geometry Name',
    "type": 'GeometryNodeSetGeometryName',
    "category": 'Other',
    "description": 'Set the name of a geometry for easier debugging',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetGreasePencilDepth': {
    "name": 'Set Grease Pencil Depth',
    "type": 'GeometryNodeSetGreasePencilDepth',
    "category": 'Other',
    "description": 'Set the Grease Pencil depth order to use',
    "inputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetGreasePencilSoftness': {
    "name": 'Set Grease Pencil Softness',
    "type": 'GeometryNodeSetGreasePencilSoftness',
    "category": 'Other',
    "description": 'Set softness attribute on Grease Pencil geometry',
    "inputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Softness', "identifier": 'Softness', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Grease Pencil', "identifier": 'Grease Pencil', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetID': {
    "name": 'Set ID',
    "type": 'GeometryNodeSetID',
    "category": 'Other',
    "description": 'Set the id attribute on the input geometry, mainly used internally for randomizing',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'ID', "identifier": 'ID', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetPointRadius': {
    "name": 'Set Point Radius',
    "type": 'GeometryNodeSetPointRadius',
    "category": 'Other',
    "description": 'Set the display size of point cloud points',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.05000000074505806}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetPosition': {
    "name": 'Set Position',
    "type": 'GeometryNodeSetPosition',
    "category": 'Other',
    "description": 'Set the location of each point',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Offset', "identifier": 'Offset', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetShadeSmooth': {
    "name": 'Set Shade Smooth',
    "type": 'GeometryNodeSetShadeSmooth',
    "category": 'Other',
    "description": 'Control the smoothness of mesh normals around each face by changing the "shade smooth" attribute',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Shade Smooth', "identifier": 'Shade Smooth', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetSplineCyclic': {
    "name": 'Set Spline Cyclic',
    "type": 'GeometryNodeSetSplineCyclic',
    "category": 'Other',
    "description": 'Control whether each spline loops back on itself by changing the "cyclic" attribute',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Cyclic', "identifier": 'Cyclic', "type": 'BOOLEAN', "default_value": False}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSetSplineResolution': {
    "name": 'Set Spline Resolution',
    "type": 'GeometryNodeSetSplineResolution',
    "category": 'Other',
    "description": 'Control how many evaluated points should be generated on every curve segment',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Resolution', "identifier": 'Resolution', "type": 'INT', "default_value": 12}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSortElements': {
    "name": 'Sort Elements',
    "type": 'GeometryNodeSortElements',
    "category": 'Other',
    "description": 'Rearrange geometry elements, changing their indices',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Group ID', "identifier": 'Group ID', "type": 'INT', "default_value": 0},
        {"name": 'Sort Weight', "identifier": 'Sort Weight', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSplineLength': {
    "name": 'Spline Length',
    "type": 'GeometryNodeSplineLength',
    "category": 'Other',
    "description": 'Retrieve the total length of each spline, as a distance or as a number of points',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE'},
        {"name": 'Point Count', "identifier": 'Point Count', "type": 'INT'}
    ],
},
    'GeometryNodeSplineParameter': {
    "name": 'Spline Parameter',
    "type": 'GeometryNodeSplineParameter',
    "category": 'Other',
    "description": 'Retrieve how far along each spline a control point is',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Factor', "identifier": 'Factor', "type": 'VALUE'},
        {"name": 'Length', "identifier": 'Length', "type": 'VALUE'},
        {"name": 'Index', "identifier": 'Index', "type": 'INT'}
    ],
},
    'GeometryNodeSplitEdges': {
    "name": 'Split Edges',
    "type": 'GeometryNodeSplitEdges',
    "category": 'Other',
    "description": 'Duplicate mesh edges and break connections with the surrounding faces',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeStoreNamedGrid': {
    "name": 'Store Named Grid',
    "type": 'GeometryNodeStoreNamedGrid',
    "category": 'Other',
    "description": 'Store grid data in a volume geometry with the specified name',
    "inputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'},
        {"name": 'Name', "identifier": 'Name', "type": 'STRING', "default_value": ''},
        {"name": 'Grid', "identifier": 'Grid', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeStringJoin': {
    "name": 'Join Strings',
    "type": 'GeometryNodeStringJoin',
    "category": 'Other',
    "description": 'Combine any number of input strings',
    "inputs": [
        {"name": 'Delimiter', "identifier": 'Delimiter', "type": 'STRING', "default_value": ''},
        {"name": 'Strings', "identifier": 'Strings', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'String', "identifier": 'String', "type": 'STRING'}
    ],
},
    'GeometryNodeSubdivisionSurface': {
    "name": 'Subdivision Surface',
    "type": 'GeometryNodeSubdivisionSurface',
    "category": 'Other',
    "description": 'Divide mesh faces to form a smooth surface, using the Catmull-Clark subdivision method',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Level', "identifier": 'Level', "type": 'INT', "default_value": 1},
        {"name": 'Edge Crease', "identifier": 'Edge Crease', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Vertex Crease', "identifier": 'Vertex Crease', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Limit Surface', "identifier": 'Limit Surface', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeSwitch': {
    "name": 'Switch',
    "type": 'GeometryNodeSwitch',
    "category": 'Other',
    "description": 'Switch between two inputs',
    "inputs": [
        {"name": 'Switch', "identifier": 'Switch', "type": 'BOOLEAN', "default_value": False},
        {"name": 'False', "identifier": 'False', "type": 'GEOMETRY'},
        {"name": 'True', "identifier": 'True', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Output', "identifier": 'Output', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeTool3DCursor': {
    "name": '3D Cursor',
    "type": 'GeometryNodeTool3DCursor',
    "category": 'Other',
    "description": "The scene's 3D cursor location and rotation",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Location', "identifier": 'Location', "type": 'VECTOR'},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION'}
    ],
},
    'GeometryNodeToolActiveElement': {
    "name": 'Active Element',
    "type": 'GeometryNodeToolActiveElement',
    "category": 'Other',
    "description": 'Active element indices of the edited geometry, for tool execution',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Index', "identifier": 'Index', "type": 'INT'},
        {"name": 'Exists', "identifier": 'Exists', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeToolFaceSet': {
    "name": 'Face Set',
    "type": 'GeometryNodeToolFaceSet',
    "category": 'Other',
    "description": "Each face's sculpt face set value",
    "inputs": [

    ],
    "outputs": [
        {"name": 'Face Set', "identifier": 'Face Set', "type": 'INT'},
        {"name": 'Exists', "identifier": 'Exists', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeToolMousePosition': {
    "name": 'Mouse Position',
    "type": 'GeometryNodeToolMousePosition',
    "category": 'Other',
    "description": 'Retrieve the position of the mouse cursor',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Mouse X', "identifier": 'Mouse X', "type": 'INT'},
        {"name": 'Mouse Y', "identifier": 'Mouse Y', "type": 'INT'},
        {"name": 'Region Width', "identifier": 'Region Width', "type": 'INT'},
        {"name": 'Region Height', "identifier": 'Region Height', "type": 'INT'}
    ],
},
    'GeometryNodeToolSelection': {
    "name": 'Selection',
    "type": 'GeometryNodeToolSelection',
    "category": 'Other',
    "description": 'User selection of the edited geometry, for tool execution',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Boolean', "identifier": 'Selection', "type": 'BOOLEAN'},
        {"name": 'Float', "identifier": 'Float', "type": 'VALUE'}
    ],
},
    'GeometryNodeToolSetFaceSet': {
    "name": 'Set Face Set',
    "type": 'GeometryNodeToolSetFaceSet',
    "category": 'Other',
    "description": 'Set sculpt face set values for faces',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Face Set', "identifier": 'Face Set', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeToolSetSelection': {
    "name": 'Set Selection',
    "type": 'GeometryNodeToolSetSelection',
    "category": 'Other',
    "description": 'Set selection of the edited geometry, for tool execution',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeTree': {
    "name": 'Geometry Node Tree',
    "type": 'GeometryNodeTree',
    "category": 'Other',
    "description": 'Node tree consisting of linked nodes used for geometries',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeTriangulate': {
    "name": 'Triangulate',
    "type": 'GeometryNodeTriangulate',
    "category": 'Other',
    "description": 'Convert all faces in a mesh to triangular faces',
    "inputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'Mesh', "identifier": 'Mesh', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeUVPackIslands': {
    "name": 'Pack UV Islands',
    "type": 'GeometryNodeUVPackIslands',
    "category": 'Other',
    "description": 'Scale islands of a UV map and move them so they fill the UV space as much as possible',
    "inputs": [
        {"name": 'UV', "identifier": 'UV', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Margin', "identifier": 'Margin', "type": 'VALUE', "default_value": 0.0010000000474974513},
        {"name": 'Rotate', "identifier": 'Rotate', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'UV', "identifier": 'UV', "type": 'VECTOR'}
    ],
},
    'GeometryNodeUVUnwrap': {
    "name": 'UV Unwrap',
    "type": 'GeometryNodeUVUnwrap',
    "category": 'Other',
    "description": 'Generate a UV map based on seam edges',
    "inputs": [
        {"name": 'Selection', "identifier": 'Selection', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Seam', "identifier": 'Seam', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Margin', "identifier": 'Margin', "type": 'VALUE', "default_value": 0.0010000000474974513},
        {"name": 'Fill Holes', "identifier": 'Fill Holes', "type": 'BOOLEAN', "default_value": True}
    ],
    "outputs": [
        {"name": 'UV', "identifier": 'UV', "type": 'VECTOR'}
    ],
},
    'GeometryNodeVertexOfCorner': {
    "name": 'Vertex of Corner',
    "type": 'GeometryNodeVertexOfCorner',
    "category": 'Other',
    "description": 'Retrieve the vertex each face corner is attached to',
    "inputs": [
        {"name": 'Corner Index', "identifier": 'Corner Index', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Vertex Index', "identifier": 'Vertex Index', "type": 'INT'}
    ],
},
    'GeometryNodeViewer': {
    "name": 'Viewer',
    "type": 'GeometryNodeViewer',
    "category": 'Other',
    "description": 'Display the input data in the Spreadsheet Editor',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Value', "identifier": 'Value', "type": 'VALUE', "default_value": 0.0}
    ],
    "outputs": [

    ],
},
    'GeometryNodeWarning': {
    "name": 'Warning',
    "type": 'GeometryNodeWarning',
    "category": 'Other',
    "description": 'Create custom warnings in node groups',
    "inputs": [
        {"name": 'Show', "identifier": 'Show', "type": 'BOOLEAN', "default_value": True},
        {"name": 'Message', "identifier": 'Message', "type": 'STRING', "default_value": ''}
    ],
    "outputs": [
        {"name": 'Show', "identifier": 'Show', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeClosureOutput': {
    "name": 'Closure Output',
    "type": 'GeometryNodeClosureOutput',
    "category": 'Output',
    "description": '',
    "inputs": [
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Closure', "identifier": 'Closure', "type": 'CLOSURE'}
    ],
},
    'GeometryNodeForeachGeometryElementOutput': {
    "name": 'For Each Geometry Element Output',
    "type": 'GeometryNodeForeachGeometryElementOutput',
    "category": 'Output',
    "description": '',
    "inputs": [
        {"name": '', "identifier": '__extend__main', "type": 'CUSTOM'},
        {"name": 'Geometry', "identifier": 'Generation_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__generation', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__main', "type": 'CUSTOM'},
        {"name": 'Geometry', "identifier": 'Generation_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__generation', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeRepeatOutput': {
    "name": 'Repeat Output',
    "type": 'GeometryNodeRepeatOutput',
    "category": 'Output',
    "description": '',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeSimulationOutput': {
    "name": 'Simulation Output',
    "type": 'GeometryNodeSimulationOutput',
    "category": 'Output',
    "description": 'Output data from the simulation zone',
    "inputs": [
        {"name": 'Skip', "identifier": 'Skip', "type": 'BOOLEAN', "default_value": False},
        {"name": 'Geometry', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Item_0', "type": 'GEOMETRY'},
        {"name": '', "identifier": '__extend__', "type": 'CUSTOM'}
    ],
},
    'GeometryNodeImageTexture': {
    "name": 'Image Texture',
    "type": 'GeometryNodeImageTexture',
    "category": 'Texture',
    "description": 'Sample values from an image texture',
    "inputs": [
        {"name": 'Image', "identifier": 'Image', "type": 'IMAGE', "default_value": None},
        {"name": 'Vector', "identifier": 'Vector', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Frame', "identifier": 'Frame', "type": 'INT', "default_value": 0}
    ],
    "outputs": [
        {"name": 'Color', "identifier": 'Color', "type": 'RGBA'},
        {"name": 'Alpha', "identifier": 'Alpha', "type": 'VALUE'}
    ],
},
    'GeometryNodeGizmoTransform': {
    "name": 'Transform Gizmo',
    "type": 'GeometryNodeGizmoTransform',
    "category": 'Transform',
    "description": 'Show a transform gizmo in the viewport',
    "inputs": [
        {"name": 'Value', "identifier": 'Value', "type": 'MATRIX'},
        {"name": 'Position', "identifier": 'Position', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION', "default_value": [0.0, 0.0, 0.0]}
    ],
    "outputs": [
        {"name": 'Transform', "identifier": 'Transform', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeTransform': {
    "name": 'Transform Geometry',
    "type": 'GeometryNodeTransform',
    "category": 'Transform',
    "description": 'Translate, rotate or scale the geometry',
    "inputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'},
        {"name": 'Translation', "identifier": 'Translation', "type": 'VECTOR', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Rotation', "identifier": 'Rotation', "type": 'ROTATION', "default_value": [0.0, 0.0, 0.0]},
        {"name": 'Scale', "identifier": 'Scale', "type": 'VECTOR', "default_value": [1.0, 1.0, 1.0]},
        {"name": 'Transform', "identifier": 'Transform', "type": 'MATRIX'}
    ],
    "outputs": [
        {"name": 'Geometry', "identifier": 'Geometry', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeViewportTransform': {
    "name": 'Viewport Transform',
    "type": 'GeometryNodeViewportTransform',
    "category": 'Transform',
    "description": 'Retrieve the view direction and location of the 3D viewport',
    "inputs": [

    ],
    "outputs": [
        {"name": 'Projection', "identifier": 'Projection', "type": 'MATRIX'},
        {"name": 'View', "identifier": 'View', "type": 'MATRIX'},
        {"name": 'Is Orthographic', "identifier": 'Is Orthographic', "type": 'BOOLEAN'}
    ],
},
    'GeometryNodeDistributePointsInVolume': {
    "name": 'Distribute Points in Volume',
    "type": 'GeometryNodeDistributePointsInVolume',
    "category": 'Volume',
    "description": 'Generate points inside a volume',
    "inputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'},
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Seed', "identifier": 'Seed', "type": 'INT', "default_value": 0},
        {"name": 'Spacing', "identifier": 'Spacing', "type": 'VECTOR', "default_value": [0.30000001192092896, 0.30000001192092896, 0.30000001192092896]},
        {"name": 'Threshold', "identifier": 'Threshold', "type": 'VALUE', "default_value": 0.10000000149011612}
    ],
    "outputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodePointsToVolume': {
    "name": 'Points to Volume',
    "type": 'GeometryNodePointsToVolume',
    "category": 'Volume',
    "description": 'Generate a fog volume sphere around every point',
    "inputs": [
        {"name": 'Points', "identifier": 'Points', "type": 'GEOMETRY'},
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Voxel Size', "identifier": 'Voxel Size', "type": 'VALUE', "default_value": 0.30000001192092896},
        {"name": 'Voxel Amount', "identifier": 'Voxel Amount', "type": 'VALUE', "default_value": 64.0},
        {"name": 'Radius', "identifier": 'Radius', "type": 'VALUE', "default_value": 0.5}
    ],
    "outputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'}
    ],
},
    'GeometryNodeVolumeCube': {
    "name": 'Volume Cube',
    "type": 'GeometryNodeVolumeCube',
    "category": 'Volume',
    "description": 'Generate a dense volume with a field that controls the density at each grid voxel based on its position',
    "inputs": [
        {"name": 'Density', "identifier": 'Density', "type": 'VALUE', "default_value": 1.0},
        {"name": 'Background', "identifier": 'Background', "type": 'VALUE', "default_value": 0.0},
        {"name": 'Min', "identifier": 'Min', "type": 'VECTOR', "default_value": [-1.0, -1.0, -1.0]},
        {"name": 'Max', "identifier": 'Max', "type": 'VECTOR', "default_value": [1.0, 1.0, 1.0]},
        {"name": 'Resolution X', "identifier": 'Resolution X', "type": 'INT', "default_value": 32},
        {"name": 'Resolution Y', "identifier": 'Resolution Y', "type": 'INT', "default_value": 32},
        {"name": 'Resolution Z', "identifier": 'Resolution Z', "type": 'INT', "default_value": 32}
    ],
    "outputs": [
        {"name": 'Volume', "identifier": 'Volume', "type": 'GEOMETRY'}
    ],
}
}

# Convenience: DSL primitive name → bpy node type
DSL_PRIMITIVE_MAP: dict[str, str] = {
    'circle': 'GeometryNodeMeshCircle',
    'cone': 'GeometryNodeMeshCone',
    'cube': 'GeometryNodeMeshCube',
    'cylinder': 'GeometryNodeMeshCylinder',
    'grid': 'GeometryNodeMeshGrid',
    'ico_sphere': 'GeometryNodeMeshIcoSphere',
    'line': 'GeometryNodeMeshLine',
    'point': 'GeometryNodePoints',
    'sphere': 'GeometryNodeMeshUVSphere',
}

# Maps bpy node type → list of input socket dicts
NODE_INPUTS: dict[str, list[dict]] = {
    bpy_type: info["inputs"] for bpy_type, info in NODE_REGISTRY.items()
}

# Maps bpy node type → list of output socket dicts
NODE_OUTPUTS: dict[str, list[dict]] = {
    bpy_type: info["outputs"] for bpy_type, info in NODE_REGISTRY.items()
}

# Maps bpy node type → human-readable name
NODE_NAMES: dict[str, str] = {
    bpy_type: info["name"] for bpy_type, info in NODE_REGISTRY.items()
}
