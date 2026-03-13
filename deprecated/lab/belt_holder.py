import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125

def create_belt_holder():
    start("belt_holder")
    
    base = cylinder(5.5, 15, "hole1" )
    hole2 = cylinder(4.5, 15, "hole2")
    
    base = difference(base, [hole2])
    
    output(base)

create_belt_holder()