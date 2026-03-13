import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

tolerance = 0.125

def create_film_spooler():
  start("film_spooler")
  
  base = cube(89, 74, 3, "base", position=(27, 0, -23/2))
  h_base = cube(5, 63.5, 5, "h_base", position=(20 + 10, 0, -23/2))
  h_base_120 = cube(33, 66 + tolerance * 2, 5, "h_base_120", position=(86/2 + 20, 0, -23/2))

  base = difference(base, [h_base, h_base_120])

  film_roll_case = cube(30, 49, 23, "film_roll_case")
  h_film_roll_case = cube(32, 44, 26, "h_film_roll_case", translation=(3, 0, 3))
  h_cyl_cub_support = cube(12, 12, 17 , "h_cyl_cub_support", translation=(0, 43/2, 23/2))
  h_cyl_support = cylinder(6, 10, "h_cyl_support", translation=(0, 43/2, 3), rotation=(90, 0, 0))
  h_film_back = cube(4, 36, 3, "h_film_back", translation=(-15, 0, -23/2 + 4))
  film_roll_case = difference(film_roll_case, [h_film_roll_case, h_cyl_support, h_cyl_cub_support, h_film_back])
  cyl_support = cylinder(5 - tolerance, 2, "cyl_support", translation=(0, -43/2, 3), rotation=(90, 0, 0))
  film_roll_case = union([film_roll_case, cyl_support])

  film_stop = cube(2, 49, 4, "film_stop", translation=(14, 0, -23/2 + 3))
  h_film_stop = cube(5, 36, 4, "h_film_stop", translation=(14, 0, -23/2 + 3))
  film_stop = difference(film_stop, [h_film_stop])

  reel = cube(10, 43, 5, "reel", translation=(23/2 + 10, 0, -23/2 + 3))
  h_reel = cube(10, 35 + tolerance * 2 , 6, "h_reel", translation=(23/2 + 10, 0, -23/2 + 3))
  reel = difference(reel, [h_reel])


  film_120_bridge = cylinder(8, 70, "film_120_bridge", translation=(86/2 + 20, 0, 1), rotation=(90, 0, 0))
  bridge_wall = cube(16, 70, 14, "bridge_wall", translation=(86/2 + 20, 0, -6))
  film_120_bridge = union([film_120_bridge, bridge_wall])
  h_film_120_bridge = cylinder(18, 66 + tolerance * 2, "h_film_120_bridge", translation=(86/2 + 20, 0, 1), rotation=(90, 0, 0))
  h_film_axis = cylinder(2.5, 100 + tolerance * 2, "h_film_axis", translation=(86/2 + 20, 0, 1), rotation=(90, 0, 0))
  film_120_bridge = difference(film_120_bridge, [h_film_120_bridge, h_film_axis])

  base = union([base, film_roll_case, reel, film_120_bridge, film_stop])


  output(base)

def create_h_base_120():
  start("h_base_120")

  h_base_120 = cube(30, 63 + tolerance * 2, 5, "h_base_120", position=(86/2 - 15 + 24, 0, -23/2))

  output(h_base_120)


create_film_spooler()
# create_h_base_120()