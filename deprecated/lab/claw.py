
import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125

def create_claw():
    start("claw")
    c_sprocket = 4.7498

    leg_l = cube(5.5, 50, 2, "base", position=(14.75, 0, 0))
    leg_r = cube(5.5, 50, 2, "base", position=(-14.75, 0, 0))
    top = cube(35, 10, 2, "top", position=(0, 25, 0))

    hook = cylinder(12, 2, "hook", position=(0, 35, 0), rotation=(0, 0, 0))
    h_hook = cylinder(8, 2, "h_hook", position=(0, 35, 0), rotation=(0, 0, 0))
    h_hook_2 = cube(20, 16, 2, "h_hook_2", position=(10, 30, 0)) 
    hook = difference(hook, [h_hook, h_hook_2])

    sprocket = cube(2.7 - tolerance, 1.9 - tolerance, 3, "sprocket", position=(0, 0, 1))

    y_positions = [-20 + c_sprocket * i for i in range(9)]
    sprocket_positions = [
        (x, y, 0)
        for y in y_positions
        for x in [28.169/2, -28.169/2]
    ]

    sprockets = clones(sprocket, sprocket_positions)
        
    claw = union([leg_l, leg_r, top, hook, sprockets])

    output(claw)

create_claw()