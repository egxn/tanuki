from tanuki.dsl import *
from tanuki.dsl.custom import mesh_analysis

with model("dodecahedron_mesh_analysis") as ctx:
    base = dodecahedron(2, label="dodeca")
    result = mesh_analysis(base, arm_length=0.3)
    output(result)

combined_export([ctx.graph], "dodecahedron_mesh_analysis_output.py")
