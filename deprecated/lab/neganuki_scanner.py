from email.mime import base
import sys
sys.path.append("/home/egxn/Catcode/bee/src")

from bee.nodes import *

col_r = 4.925
sqr_x = 30
sqr_y = 30
tolerance = 0.125


def create_sensor_support():
    start("sensor_support")

    sensor_support = cube((sqr_x + 10) * 2  , (sqr_x + 10) * 2, 4, "sensor_support", position=(0, 0, -15))
    
    column1 = cylinder(col_r + 2, 30, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r + 2, 30, "column2", position=(-sqr_x, sqr_y, 0))
    column3 = cylinder(col_r + 2, 30, "column3", position=(sqr_x, -sqr_y, 0))
    column4 = cylinder(col_r + 2, 30, "column4", position=(-sqr_x, -sqr_y, 0))

    h_column1 = cylinder(col_r + tolerance, 30, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance, 30, "column2", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance, 30, "column3", position=(sqr_x, -sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance, 30, "column4", position=(-sqr_x, -sqr_y, 0))

    sensor_col1 = cylinder(4, 6, "sensor_col1", position=(17, 17, -11))
    sensor_col2 = cylinder(4, 6, "sensor_col2", position=(-17, 17, -11))
    sensor_col3 = cylinder(4, 6, "sensor_col3", position=(17, -17, -11))
    sensor_col4 = cylinder(4, 6, "sensor_col4", position=(-17, -17, -11))

    h_sensor_col1 = cylinder(2 - tolerance, 6, "h_sensor_col1", position=(17, 17, -11))
    h_sensor_col2 = cylinder(2 - tolerance, 6, "h_sensor_col2", position=(-17, 17, -11))
    h_sensor_col3 = cylinder(2 - tolerance, 6, "h_sensor_col3", position=(17, -17, -11))
    h_sensor_col4 = cylinder(2 - tolerance, 6, "h_sensor_col4", position=(-17, -17, -11))

    sensor_support = union([sensor_support, column1, column2, column3, column4  , sensor_col1, sensor_col2, sensor_col3, sensor_col4])
    sensor_support = difference(sensor_support, [h_column1, h_column2, h_column3, h_column4, h_sensor_col1, h_sensor_col2, h_sensor_col3, h_sensor_col4])

    t_sensor_support = transform(sensor_support, rotation=(0, 180, 0), translation=(0, 0, 170))

    output(t_sensor_support)

def create_lens_support():
    start("lens_support")

    lens_support = cube((sqr_x + 10) * 2  , (sqr_x + 10) * 2, 4, "lens_support", position=(0, 0, 15))
    
    column1 = cylinder(col_r + 2, 30, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r + 2, 30, "column2", position=(-sqr_x, sqr_y, 0))
    column3 = cylinder(col_r + 2, 30, "column3", position=(sqr_x, -sqr_y, 0))
    column4 = cylinder(col_r + 2, 30, "column4", position=(-sqr_x, -sqr_y, 0))

    h_column1 = cylinder(col_r + tolerance, 50, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance, 50, "column2", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance, 50, "column3", position=(sqr_x, -sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance, 50, "column4", position=(-sqr_x, -sqr_y, 0))
    h_lens = cylinder(39.25 / 2, 30, "h_lens", position=(0, 0, 15))

    lens_support = union([lens_support, column1, column2, column3, column4])
    lens_support = difference(lens_support, [h_column1, h_column2, h_column3, h_column4, h_lens])

    t_lens_support = transform(lens_support, translation=(0, 0, 100), rotation=(180, 0, 0))

    output(t_lens_support)

def create_columns():
    start("columns")

    column1 = cylinder(col_r, 200, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r, 200, "column2", position=(-sqr_x, sqr_y, 0))
    column3 = cylinder(col_r, 200, "column3", position=(sqr_x, -sqr_y, 0))
    column4 = cylinder(col_r, 200, "column4", position=(-sqr_x, -sqr_y, 0))

    columns = union([column1, column2, column3, column4])

    t_columns = transform(columns, translation=(0, 0, 70))

    output(t_columns)

def create_film_support():
    start("film_support")

    film_support = cube(100, 60, 4, "film_support", position=(0, 0, 15))
    film_tab_1 = cube(100, 7, 1, "film_tab", position=(0, 20, 4.5))
    film_tab_2 = cube(100, 7, 1, "film_tab", position=(0, -20, 4.5))

    film_35mm = cube(100, 60, 10, "film_35mm", position=(0, 0, 9))
    h_film_35mm = cube(120, 46.5, 10, "h_film_35mm", position=(0, 0, 9))
    h_film_35mm_3 = cylinder(15, 8, "h_film_35mm_3", position=(0, 30, 9))
    h_film_35mm_4 = cylinder(15, 8, "h_film_35mm_4", position=(0, 38, 8))

    film_35mm = difference(film_35mm, [h_film_35mm])

    column1 = cylinder(col_r + 2, 13, "column1", position=(sqr_x, sqr_y,   10.5))
    column2 = cylinder(col_r + 2, 13, "column2", position=(-sqr_x, sqr_y,  10.5))
    column3 = cylinder(col_r + 2, 13, "column3", position=(sqr_x, -sqr_y,  10.5))
    column4 = cylinder(col_r + 2, 13, "column4", position=(-sqr_x, -sqr_y, 10.5))

    h_column1 = cylinder(col_r + tolerance * 2, 50, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance * 2, 50, "column2", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance * 2, 50, "column3", position=(sqr_x, -sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance * 2, 50, "column4", position=(-sqr_x, -sqr_y, 0))
    h_light = cube(80, 38, 30, "h_light", position=(0, 0, 15))

    film_support = union([film_support, column1, column2, column3, column4, film_35mm, film_tab_1, film_tab_2])
    film_support = difference(film_support, [h_column1, h_column2, h_column3, h_column4, h_light, h_film_35mm_3, h_film_35mm_4])
    t_film_support = transform(film_support, translation=(0, 0, 1))

    output(t_film_support)

def create_film_support_base():
    start("film_support_base")

    film_support_base = cube(44, 10, 10, "film_support_base", position=(0, 0, 0))
    h_film_support_base = cube(41 + tolerance * 2, 7 + tolerance * 2, 10, "h_film_support_base", position=(0, 0, 1))

    film_support_base = difference(film_support_base, [h_film_support_base])

    output(film_support_base)

def create_film():
    start("film")

    film_35mm = cube(230, 41, 7, "film_35mm", position=(0, 0, 0))

    x_magnet = 220 / 2
    r_magnet = 2.5 + tolerance

    magnet_1 = cylinder(r_magnet, 3, "h_magnet_1", position=(x_magnet, 0,  0.5))
    magnet_2 = cylinder(r_magnet, 3, "h_magnet_2", position=(x_magnet, 10, 0.5))
    magnet_3 = cylinder(r_magnet, 3, "h_magnet_3", position=(x_magnet, -10, 0.5))
    magnet_5 = cylinder(r_magnet, 3, "h_magnet_5", position=(-x_magnet, 0, 0.5))
    magnet_6 = cylinder(r_magnet, 3, "h_magnet_6", position=(-x_magnet, 10, 0.5))
    magnet_7 = cylinder(r_magnet, 3, "h_magnet_7", position=(-x_magnet, -10, 0.5))

    h_film = cube(210, 30, 7, "h_film", position=(0, 0, 0))

    film_35mm = difference(film_35mm, [magnet_1, magnet_2, magnet_3, magnet_5, magnet_6, magnet_7, h_film])
    t_film_35mm = transform(film_35mm, translation=(0, 0, 10))

    output(t_film_35mm)

def create_dummy_stepper():
    start("dummy_stepper")

    stepper = cylinder(14, 19, "stepper", position=(0, 0, 0))
    wires = cube(19, 10, 19, "wires", position=(0, -10, 0))

    connector_cyl = cylinder(5.8/2, 10, "connector", position=(0, 0, (19/2) + 5))
    connector_cube = cube(6, 3.8, 10, "connector", position=(0, 0, (19/2) + 5))
    connector = intersect([connector_cyl, connector_cube])
    t_connector = transform(connector, translation=(0, 8, 0))

    screws_base = cube(35, 4, 1, "screws_base", position=(0, 0, 19/2 - 0.5))

    stepper = union([stepper, wires, t_connector, screws_base])
    t_stepper = transform(stepper, translation=(0, 40, -11), rotation=(0, 0, 180))

    output(t_stepper)

def create_motor_support():
    start("motor_support")
 
    motor_support = cube((sqr_x + 20) * 2  , 10 , 12, "motor_support", position=(0, 25, 0))

    column3 = cylinder(col_r + 2, 12, "column3", position=(sqr_x, sqr_y,  0))
    column4 = cylinder(col_r + 2, 12, "column4", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance * 2, 50, "column3", position=(sqr_x, sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance * 2, 50, "column4", position=(-sqr_x, sqr_y, 0))
    h_motor = cylinder(15, 12, "h_motor", position=(0, 38, 0))

    screw_base_1 = cube(8, 20, 6, "screw_base_1", position=(35/2,  30, -3))
    screw_base_2 = cube(8, 20, 6, "screw_base_2", position=(-35/2, 30, -3))
    screw_col_1 = cylinder(4, 7.5, "screw_col_1", position=(35/2,  40, -2.25))
    screw_col_2 = cylinder(4, 7.5, "screw_col_2", position=(-35/2, 40, -2.25))

    h_screw_col_1 = cylinder(2 + tolerance, 6, "h_screw_col_1", position=(35/2,  40, -1.5))
    h_screw_col_2 = cylinder(2 + tolerance, 6, "h_screw_col_2", position=(-35/2, 40, -1.5))

    motor_support = union([motor_support, column3, column4, screw_base_1, screw_base_2, screw_col_1, screw_col_2])
    motor_support = difference(motor_support, [h_column3, h_column4, h_motor, h_screw_col_1, h_screw_col_2])

    t_motor_support = transform(motor_support, rotation=(0, 180, 0))

    output(t_motor_support)

def create_h_motor_cog():
    start("h_motor_cog")

    connector_cyl = cylinder(5/2, 30, "connector", position=(0, 0, 0))
    connector_cube = cube(6 + tolerance, 3.8, 30, "connector", position=(0, 0, 0))
    connector = intersect([connector_cyl, connector_cube])

    output(connector)

def create_tol_cyl():
    start("tol_cyl")
    
    column1 = cylinder(col_r + 2, 20, "column1", position=(sqr_x, sqr_y, 0))
    h_column1 = cylinder(col_r + tolerance, 20, "column1", position=(sqr_x, sqr_y, 0))

    tol_cyl = difference(column1, [h_column1])

    output(tol_cyl)

def create_spacer():
    start("spacer")

    spacer = cylinder(col_r + 2, 10, "spacer1", position=(0, 0, 0))
    h_spacer = cylinder((col_r - 0.2) + tolerance, 15, "spacer1", position=(0, 0, 0))
    h_spacer_2 = cube(10, 8, 15, "h_spacer_2", position=(col_r + 2 / 2, 0, 0))

    spacer = difference(spacer, [h_spacer, h_spacer_2])

    output(spacer)

def create_lamp_support_1():
    start("lamp_support_1")

    lamp_support_0 = cube(90, 90, 4, "lamp_support", position=(0, 0, 10))
    
    column1 = cylinder(col_r + 2, 20, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r + 2, 20, "column2", position=(-sqr_x, sqr_y, 0))
    column3 = cylinder(col_r + 2, 20, "column3", position=(sqr_x, -sqr_y, 0))
    column4 = cylinder(col_r + 2, 20, "column4", position=(-sqr_x, -sqr_y, 0))

    h_column1 = cylinder(col_r + tolerance, 20, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance, 20, "column2", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance, 20, "column3", position=(sqr_x, -sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance, 20, "column4", position=(-sqr_x, -sqr_y, 0))

    h_supp_column1 = cylinder(3 + tolerance, 30, "column1",vertices=8, position=(40, 40, 24))
    h_supp_column2 = cylinder(3 + tolerance, 30, "column2",vertices=8, position=(-40, 40, 24))
    h_supp_column3 = cylinder(3 + tolerance, 30, "column3",vertices=8, position=(40, -40, 24))
    h_supp_column4 = cylinder(3 + tolerance, 30, "column4",vertices=8, position=(-40, -40, 24))

    h_lamp_0 = cylinder(36, 20, "h_lamp", position=(0, 0, 15))

    lamp_support = union([column1, column2, column3, column4, lamp_support_0])
    lamp_support = difference(lamp_support, [h_column1, h_column2, h_column3, h_column4, h_lamp_0, h_supp_column1, h_supp_column2, h_supp_column3, h_supp_column4])

    t_lamp_support = transform(lamp_support, translation=(0, 0, -40), rotation=(180, 0, 0))

    output(t_lamp_support)

def create_lamp_support_2():
    start("lamp_support_2")

    lamp_support = cube(90, 90, 3, "lamp_support", position=(0, 0, -8))

    column1 = cylinder(col_r + 2, 15, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r + 2, 15, "column2", position=(-sqr_x, sqr_y, 0))
    column3 = cylinder(col_r + 2, 15, "column3", position=(sqr_x, -sqr_y, 0))
    column4 = cylinder(col_r + 2, 15, "column4", position=(-sqr_x, -sqr_y, 0))

    h_column1 = cylinder(col_r + tolerance, 25, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance, 25, "column2", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance, 25, "column3", position=(sqr_x, -sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance, 25, "column4", position=(-sqr_x, -sqr_y, 0))

    h_lamp_1 = cylinder(20.5/2 + tolerance, 3, "h_lamp", position=(0, -16, -7))
    h_lamp_2 = cylinder(20.5/2 + tolerance, 3, "h_lamp", position=(-12, 10, -7))
    h_lamp_3 = cylinder(20.5/2 + tolerance, 3, "h_lamp", position=(12, 10, -7))
    h_lamp_4 = cylinder(4, 10, "h_lamp", position=(0, 0, -7))

    lamp_support = union([lamp_support, column1, column2, column3, column4])
    lamp_support = difference(lamp_support, [h_column1, h_column2, h_column3, h_column4, h_lamp_1, h_lamp_2, h_lamp_3, h_lamp_4])

    t_lamp_support = transform(lamp_support, translation=(0, 0, -40), rotation=(180, 0, 0))

    output(t_lamp_support)

def create_dummy_lamp():
    start("dummy_lamp")

    lamp = cylinder(86/2, 25, "lamp", position=(0, 0, -65.5))

    output(lamp)

def create_cam_tripod_support():
    start("create_cam_tripod_support")

    base = cube(sqr_x * 2, 10, 20, "base", position=(0,sqr_y,0))
    column1 = cylinder(col_r + 2, 20, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r + 2, 20, "column2", position=(-sqr_x, sqr_y, 0))

    h_column1 = cylinder(col_r + tolerance, 35, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance, 35, "column2", position=(-sqr_x, sqr_y, 0))
    h_screw = cylinder(4, 30, "h_screw",position=(0,sqr_y,0), rotation=(0, 90, 90))

    cam_support = union([base, column1, column2])
    cam_support = difference(cam_support, [h_column1, h_column2, h_screw])

    t_cam_support = transform(cam_support, translation=(0, 0, 40))


    output(t_cam_support)


def create_sensor_support_j1():
    start("sensor_support_j1")

    sensor_support = cube((sqr_x + 10) * 2  , (sqr_x + 10) * 2, 4, "sensor_support", position=(0, 0, -15))
    
    h_column1 = cylinder(col_r + tolerance, 100, "column1", position=(sqr_x, sqr_y, 0))
    h_column2 = cylinder(col_r + tolerance, 100, "column2", position=(-sqr_x, sqr_y, 0))
    h_column3 = cylinder(col_r + tolerance, 100, "column3", position=(sqr_x, -sqr_y, 0))
    h_column4 = cylinder(col_r + tolerance, 100, "column4", position=(-sqr_x, -sqr_y, 0))

    sensor_support = union([sensor_support])
    sensor_support = difference(sensor_support, [h_column1, h_column2, h_column3, h_column4])

    t_sensor_support = transform(sensor_support, rotation=(0, 180, 0), translation=(0, 0, 170))

    output(t_sensor_support)

def create_sensor_support_j1_column():
    start("sensor_support_j1_column")

    column1 = cylinder(col_r + (tolerance/2), 10, "column1", position=(0, 0, 7.5))
    column2 = cylinder(col_r + 4, 15, "column2", position=(0, 0, 0))
    h_column3 = cylinder(col_r, 15, "column3", position=(0, 0, -5))

    column = union([column1, column2])
    column = difference(column, [h_column3])

    output(column)

def create_base_cam():
    start("base_cam")

    base_cam = cube(50, 50, 10, "base_cam", position=(0, 0, 0))

    h_nonslip_1 = cylinder(4, 6, "h_nonslip", position=(18, 18, -4))
    h_nonslip_2 = cylinder(4, 6, "h_nonslip", position=(-18, 18, -4))
    h_nonslip_3 = cylinder(4, 6, "h_nonslip", position=(18, -18, -4))
    h_nonslip_4 = cylinder(4, 6, "h_nonslip", position=(-18, -18, -4))

    base_colum_1 = cube(14, 14, 20, "base_columns", position=(18, 15, 12))
    h_column_1 = cylinder(col_r, 13, "column3", position=(19, 15, 16), rotation=(90, 0, 90))
    base_colum_1 = difference(base_colum_1, [h_column_1])

    base_colum_2 = transform(base_colum_1, translation=(0, -30, 0))

    h_screw_1 = cylinder(4, 30, "h_screw")
    h_screw_2 = cylinder(8, 6, "h_screw", position=(0, 0, -2))

    h_light = cube(21, 50, 10, "h_light", position=(0, 0, 8))

    base_cam = difference(base_cam, [h_nonslip_1, h_nonslip_2, h_nonslip_3, h_nonslip_4, h_screw_1, h_screw_2, h_light])
    base_cam = union([base_cam, base_colum_1, base_colum_2])

    output(base_cam)

def create_cover():
    start("cover")

    base_1 = cube(sqr_x * 2, 5, 10, "base", position=(0, sqr_y, 0))
    base_2 = cube(sqr_x * 2, 5, 10, "base", position=(0, -sqr_y, 0))
    base_3 = cube(5, sqr_y * 2, 10, "base", position=(sqr_x, 0, 0))
    base_4 = cube(5, sqr_y * 2, 10, "base", position=(-sqr_x, 0, 0))

    column1 = cylinder(col_r + 2, 10, "column1", position=(sqr_x, sqr_y, 0))
    column2 = cylinder(col_r + 2, 10, "column2", position=(-sqr_x, sqr_y, 0))
    column3 = cylinder(col_r + 2, 10, "column3", position=(sqr_x, -sqr_y, 0))
    column4 = cylinder(col_r + 2, 10, "column4", position=(-sqr_x, -sqr_y, 0))

    h_column1 = cylinder(col_r, 10, "column1", position=(sqr_x, sqr_y, 2))
    h_column2 = cylinder(col_r, 10, "column2", position=(-sqr_x, sqr_y, 2))
    h_column3 = cylinder(col_r, 10, "column3", position=(sqr_x, -sqr_y, 2))
    h_column4 = cylinder(col_r, 10, "column4", position=(-sqr_x, -sqr_y, 2))

    cover = union([base_1, base_2, base_3, base_4, column1, column2, column3, column4])
    cover = difference(cover, [h_column1, h_column2, h_column3, h_column4])

    t_cover = transform(cover, translation=(0, 0, 40))

    output(t_cover)

def create_film_slider():
    start("film_slider")

    slider_base = cube((sqr_x + 10) * 2, (sqr_x + 10) * 2, 5, "slider_base")

    h_slider_1 = cube(40, 34.5, 30, "h_slider")
    h_slider_2 = cube(160, 35 + tolerance, 0.5, "h_slider", position=(0, 0, -2.25))

    h_column1 = cylinder(col_r + tolerance, 20, "column1", position=(sqr_x, sqr_y, 2))
    h_column2 = cylinder(col_r + tolerance, 20, "column2", position=(-sqr_x, sqr_y, 2))
    h_column3 = cylinder(col_r + tolerance, 20, "column3", position=(sqr_x, -sqr_y, 2))
    h_column4 = cylinder(col_r + tolerance, 20, "column4", position=(-sqr_x, -sqr_y, 2))

    join_1 = cube(40, 3, 3, "join_1", position=(0, 20, -4))
    join_2 = cube(40, 3, 3, "join_1", position=(0, -20, -4))

    slider = difference(slider_base, [h_slider_1, h_slider_2, h_column1, h_column2, h_column3, h_column4])
    slider = union([slider, join_1, join_2])

    output(slider)

def create_film_slider_2():
    start("film_slider_2")

    slider = cube(45, 45, 5, "slider", position=(0, 0, -5))
    h_slider_1 = cube(40, 34.5, 30, "h_slider")

    h_join_1 = cube(40 + tolerance, 3 + tolerance, 3 + tolerance, "join_1", position=(0, 20, -4))
    h_join_2 = cube(40 + tolerance, 3 + tolerance, 3 + tolerance, "join_1", position=(0, -20, -4))

    slider = difference(slider, [h_slider_1, h_join_1, h_join_2])

    output(slider)

# create_sensor_support()
create_lens_support()
# create_spacer()
# create_columns()
# create_film()
# create_film_support()
# create_dummy_stepper()
# create_motor_support()
# create_h_motor_cog()
# create_film_support_base()
# create_tol_cyl()
# create_lamp_support_1()
# create_lamp_support_2()
# create_dummy_lamp()
# create_cam_tripod_support()
# create_sensor_support_j1()
# create_sensor_support_j1_column()
# create_base_cam()
# create_cover()
# create_film_slider()
# create_film_slider_2()