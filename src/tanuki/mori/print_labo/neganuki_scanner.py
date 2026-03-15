"""Neganuki scanner — full film scanner assembly with 20+ parts."""

from tanuki.dsl import *

col_r = 4.925
sqr_x = 30
sqr_y = 30
tolerance = 0.125


def create_sensor_support():
    with model("sensor_support") as ctx:
        sensor_support = cube(
            (sqr_x + 10) * 2, (sqr_x + 10) * 2, 4, "sensor_support"
        ) | place(0, 0, -15)

        column1 = cylinder(col_r + 2, 30, "column1") | place(sqr_x, sqr_y, 0)
        column2 = cylinder(col_r + 2, 30, "column2") | place(-sqr_x, sqr_y, 0)
        column3 = cylinder(col_r + 2, 30, "column3") | place(sqr_x, -sqr_y, 0)
        column4 = cylinder(col_r + 2, 30, "column4") | place(-sqr_x, -sqr_y, 0)

        h_column1 = cylinder(col_r + tolerance, 30, "column1") | place(sqr_x, sqr_y, 0)
        h_column2 = cylinder(col_r + tolerance, 30, "column2") | place(-sqr_x, sqr_y, 0)
        h_column3 = cylinder(col_r + tolerance, 30, "column3") | place(sqr_x, -sqr_y, 0)
        h_column4 = cylinder(col_r + tolerance, 30, "column4") | place(-sqr_x, -sqr_y, 0)

        sensor_col1 = cylinder(4, 6, "sensor_col1") | place(17, 17, -11)
        sensor_col2 = cylinder(4, 6, "sensor_col2") | place(-17, 17, -11)
        sensor_col3 = cylinder(4, 6, "sensor_col3") | place(17, -17, -11)
        sensor_col4 = cylinder(4, 6, "sensor_col4") | place(-17, -17, -11)

        h_sensor_col1 = cylinder(2 - tolerance, 6, "h_sensor_col1") | place(17, 17, -11)
        h_sensor_col2 = cylinder(2 - tolerance, 6, "h_sensor_col2") | place(-17, 17, -11)
        h_sensor_col3 = cylinder(2 - tolerance, 6, "h_sensor_col3") | place(17, -17, -11)
        h_sensor_col4 = cylinder(2 - tolerance, 6, "h_sensor_col4") | place(-17, -17, -11)

        sensor_support = union([
            sensor_support, column1, column2, column3, column4,
            sensor_col1, sensor_col2, sensor_col3, sensor_col4,
        ])
        sensor_support = difference(sensor_support, [
            h_column1, h_column2, h_column3, h_column4,
            h_sensor_col1, h_sensor_col2, h_sensor_col3, h_sensor_col4,
        ])

        t_sensor_support = sensor_support | rotate(0, 180, 0) | translate(0, 0, 170)

        output(t_sensor_support)
    return ctx.graph


def create_lens_support():
    with model("lens_support") as ctx:
        lens_support = cube(
            (sqr_x + 10) * 2, (sqr_x + 10) * 2, 4, "lens_support"
        ) | place(0, 0, 15)

        column1 = cylinder(col_r + 2, 30, "column1") | place(sqr_x, sqr_y, 0)
        column2 = cylinder(col_r + 2, 30, "column2") | place(-sqr_x, sqr_y, 0)
        column3 = cylinder(col_r + 2, 30, "column3") | place(sqr_x, -sqr_y, 0)
        column4 = cylinder(col_r + 2, 30, "column4") | place(-sqr_x, -sqr_y, 0)

        h_column1 = cylinder(col_r + tolerance, 50, "column1") | place(sqr_x, sqr_y, 0)
        h_column2 = cylinder(col_r + tolerance, 50, "column2") | place(-sqr_x, sqr_y, 0)
        h_column3 = cylinder(col_r + tolerance, 50, "column3") | place(sqr_x, -sqr_y, 0)
        h_column4 = cylinder(col_r + tolerance, 50, "column4") | place(-sqr_x, -sqr_y, 0)
        h_lens = cylinder(39.25 / 2, 30, "h_lens") | place(0, 0, 15)

        lens_support = union([lens_support, column1, column2, column3, column4])
        lens_support = difference(
            lens_support, [h_column1, h_column2, h_column3, h_column4, h_lens]
        )

        t_lens_support = lens_support | rotate(180, 0, 0) | translate(0, 0, 100)

        output(t_lens_support)
    return ctx.graph


def create_columns():
    with model("columns") as ctx:
        column1 = cylinder(col_r, 200, "column1") | place(sqr_x, sqr_y, 0)
        column2 = cylinder(col_r, 200, "column2") | place(-sqr_x, sqr_y, 0)
        column3 = cylinder(col_r, 200, "column3") | place(sqr_x, -sqr_y, 0)
        column4 = cylinder(col_r, 200, "column4") | place(-sqr_x, -sqr_y, 0)

        columns = union([column1, column2, column3, column4])

        t_columns = columns | translate(0, 0, 70)

        output(t_columns)
    return ctx.graph


def create_film_support():
    with model("film_support") as ctx:
        film_support = cube(100, 60, 4, "film_support") | place(0, 0, 15)
        film_tab_1 = cube(100, 7, 1, "film_tab") | place(0, 20, 4.5)
        film_tab_2 = cube(100, 7, 1, "film_tab") | place(0, -20, 4.5)

        film_35mm = cube(100, 60, 10, "film_35mm") | place(0, 0, 9)
        h_film_35mm = cube(120, 46.5, 10, "h_film_35mm") | place(0, 0, 9)
        h_film_35mm_3 = cylinder(15, 8, "h_film_35mm_3") | place(0, 30, 9)
        h_film_35mm_4 = cylinder(15, 8, "h_film_35mm_4") | place(0, 38, 8)

        film_35mm = difference(film_35mm, [h_film_35mm])

        column1 = cylinder(col_r + 2, 13, "column1") | place(sqr_x, sqr_y, 10.5)
        column2 = cylinder(col_r + 2, 13, "column2") | place(-sqr_x, sqr_y, 10.5)
        column3 = cylinder(col_r + 2, 13, "column3") | place(sqr_x, -sqr_y, 10.5)
        column4 = cylinder(col_r + 2, 13, "column4") | place(-sqr_x, -sqr_y, 10.5)

        h_column1 = cylinder(col_r + tolerance * 2, 50, "column1") | place(sqr_x, sqr_y, 0)
        h_column2 = cylinder(col_r + tolerance * 2, 50, "column2") | place(-sqr_x, sqr_y, 0)
        h_column3 = cylinder(col_r + tolerance * 2, 50, "column3") | place(sqr_x, -sqr_y, 0)
        h_column4 = cylinder(col_r + tolerance * 2, 50, "column4") | place(-sqr_x, -sqr_y, 0)
        h_light = cube(80, 38, 30, "h_light") | place(0, 0, 15)

        film_support = union([
            film_support, column1, column2, column3, column4,
            film_35mm, film_tab_1, film_tab_2,
        ])
        film_support = difference(film_support, [
            h_column1, h_column2, h_column3, h_column4,
            h_light, h_film_35mm_3, h_film_35mm_4,
        ])
        t_film_support = film_support | translate(0, 0, 1)

        output(t_film_support)
    return ctx.graph


def create_film_support_base():
    with model("film_support_base") as ctx:
        film_support_base = cube(44, 10, 10, "film_support_base")
        h_film_support_base = cube(
            41 + tolerance * 2, 7 + tolerance * 2, 10, "h_film_support_base"
        ) | place(0, 0, 1)

        film_support_base = difference(film_support_base, [h_film_support_base])

        output(film_support_base)
    return ctx.graph


def create_film():
    with model("film") as ctx:
        film_35mm = cube(230, 41, 7, "film_35mm")

        x_magnet = 220 / 2
        r_magnet = 2.5 + tolerance

        magnet_1 = cylinder(r_magnet, 3, "h_magnet_1") | place(x_magnet, 0, 0.5)
        magnet_2 = cylinder(r_magnet, 3, "h_magnet_2") | place(x_magnet, 10, 0.5)
        magnet_3 = cylinder(r_magnet, 3, "h_magnet_3") | place(x_magnet, -10, 0.5)
        magnet_5 = cylinder(r_magnet, 3, "h_magnet_5") | place(-x_magnet, 0, 0.5)
        magnet_6 = cylinder(r_magnet, 3, "h_magnet_6") | place(-x_magnet, 10, 0.5)
        magnet_7 = cylinder(r_magnet, 3, "h_magnet_7") | place(-x_magnet, -10, 0.5)

        h_film = cube(210, 30, 7, "h_film")

        film_35mm = difference(
            film_35mm,
            [magnet_1, magnet_2, magnet_3, magnet_5, magnet_6, magnet_7, h_film],
        )
        t_film_35mm = film_35mm | translate(0, 0, 10)

        output(t_film_35mm)
    return ctx.graph


def create_dummy_stepper():
    with model("dummy_stepper") as ctx:
        stepper = cylinder(14, 19, "stepper")
        wires = cube(19, 10, 19, "wires") | place(0, -10, 0)

        connector_cyl = cylinder(5.8 / 2, 10, "connector") | place(0, 0, (19 / 2) + 5)
        connector_cube = cube(6, 3.8, 10, "connector") | place(0, 0, (19 / 2) + 5)
        connector = intersect([connector_cyl, connector_cube])
        t_connector = connector | translate(0, 8, 0)

        screws_base = cube(35, 4, 1, "screws_base") | place(0, 0, 19 / 2 - 0.5)

        stepper = union([stepper, wires, t_connector, screws_base])
        t_stepper = stepper | rotate(0, 0, 180) | translate(0, 40, -11)

        output(t_stepper)
    return ctx.graph


def create_motor_support():
    with model("motor_support") as ctx:
        motor_support = cube(
            (sqr_x + 20) * 2, 10, 12, "motor_support"
        ) | place(0, 25, 0)

        column3 = cylinder(col_r + 2, 12, "column3") | place(sqr_x, sqr_y, 0)
        column4 = cylinder(col_r + 2, 12, "column4") | place(-sqr_x, sqr_y, 0)
        h_column3 = cylinder(col_r + tolerance * 2, 50, "column3") | place(sqr_x, sqr_y, 0)
        h_column4 = cylinder(col_r + tolerance * 2, 50, "column4") | place(-sqr_x, sqr_y, 0)
        h_motor = cylinder(15, 12, "h_motor") | place(0, 38, 0)

        screw_base_1 = cube(8, 20, 6, "screw_base_1") | place(35 / 2, 30, -3)
        screw_base_2 = cube(8, 20, 6, "screw_base_2") | place(-35 / 2, 30, -3)
        screw_col_1 = cylinder(4, 7.5, "screw_col_1") | place(35 / 2, 40, -2.25)
        screw_col_2 = cylinder(4, 7.5, "screw_col_2") | place(-35 / 2, 40, -2.25)

        h_screw_col_1 = cylinder(2 + tolerance, 6, "h_screw_col_1") | place(35 / 2, 40, -1.5)
        h_screw_col_2 = cylinder(2 + tolerance, 6, "h_screw_col_2") | place(-35 / 2, 40, -1.5)

        motor_support = union([
            motor_support, column3, column4,
            screw_base_1, screw_base_2, screw_col_1, screw_col_2,
        ])
        motor_support = difference(
            motor_support,
            [h_column3, h_column4, h_motor, h_screw_col_1, h_screw_col_2],
        )

        t_motor_support = motor_support | rotate(0, 180, 0)

        output(t_motor_support)
    return ctx.graph


def create_h_motor_cog():
    with model("h_motor_cog") as ctx:
        connector_cyl = cylinder(5 / 2, 30, "connector")
        connector_cube = cube(6 + tolerance, 3.8, 30, "connector")
        connector = intersect([connector_cyl, connector_cube])

        output(connector)
    return ctx.graph


def create_tol_cyl():
    with model("tol_cyl") as ctx:
        column1 = cylinder(col_r + 2, 20, "column1") | place(sqr_x, sqr_y, 0)
        h_column1 = cylinder(col_r + tolerance, 20, "column1") | place(sqr_x, sqr_y, 0)

        tol_cyl = difference(column1, [h_column1])

        output(tol_cyl)
    return ctx.graph


def create_spacer():
    with model("spacer") as ctx:
        spacer = cylinder(col_r + 2, 10, "spacer1")
        h_spacer = cylinder((col_r - 0.2) + tolerance, 15, "spacer1")
        h_spacer_2 = cube(10, 8, 15, "h_spacer_2") | place(col_r + 2 / 2, 0, 0)

        spacer = difference(spacer, [h_spacer, h_spacer_2])

        output(spacer)
    return ctx.graph


def create_cam_tripod_support():
    with model("create_cam_tripod_support") as ctx:
        base = cube(sqr_x * 2, 10, 20, "base") | place(0, sqr_y, 0)
        column1 = cylinder(col_r + 2, 20, "column1") | place(sqr_x, sqr_y, 0)
        column2 = cylinder(col_r + 2, 20, "column2") | place(-sqr_x, sqr_y, 0)

        h_column1 = cylinder(col_r + tolerance, 35, "column1") | place(sqr_x, sqr_y, 0)
        h_column2 = cylinder(col_r + tolerance, 35, "column2") | place(-sqr_x, sqr_y, 0)
        h_screw = cylinder(4, 30, "h_screw") | rotate(0, 90, 90) | place(0, sqr_y, 0)

        cam_support = union([base, column1, column2])
        cam_support = difference(cam_support, [h_column1, h_column2, h_screw])

        t_cam_support = cam_support | translate(0, 0, 40)

        output(t_cam_support)
    return ctx.graph


def create_sensor_support_j1():
    with model("sensor_support_j1") as ctx:
        sensor_support = cube(
            (sqr_x + 10) * 2, (sqr_x + 10) * 2, 4, "sensor_support"
        ) | place(0, 0, -15)

        h_column1 = cylinder(col_r + tolerance, 100, "column1") | place(sqr_x, sqr_y, 0)
        h_column2 = cylinder(col_r + tolerance, 100, "column2") | place(-sqr_x, sqr_y, 0)
        h_column3 = cylinder(col_r + tolerance, 100, "column3") | place(sqr_x, -sqr_y, 0)
        h_column4 = cylinder(col_r + tolerance, 100, "column4") | place(-sqr_x, -sqr_y, 0)

        sensor_support = union([sensor_support])
        sensor_support = difference(
            sensor_support, [h_column1, h_column2, h_column3, h_column4]
        )

        t_sensor_support = sensor_support | rotate(0, 180, 0) | translate(0, 0, 170)

        output(t_sensor_support)
    return ctx.graph

def create_sensor_support_mark_ii():
    with model("sensor_support_mark_ii") as ctx:
        sensor_support = cube(
            (sqr_x + 10) * 2, (sqr_x + 10) * 2, 4, "sensor_support"
        ) | place(0, 0, -15)

        h_column1 = cylinder(col_r + tolerance, 100, "column1") | place(sqr_x, sqr_y, 0)
        h_column2 = cylinder(col_r + tolerance, 100, "column2") | place(-sqr_x, sqr_y, 0)
        h_column3 = cylinder(col_r + tolerance, 100, "column3") | place(sqr_x, -sqr_y, 0)
        h_column4 = cylinder(col_r + tolerance, 100, "column4") | place(-sqr_x, -sqr_y, 0)

        sensor_support = union([sensor_support])
        sensor_support = difference(
            sensor_support, [h_column1, h_column2, h_column3, h_column4]
        )

        t_sensor_support = sensor_support | rotate(0, 180, 0) | translate(0, 0, 170)

        output(t_sensor_support)
    return ctx.graph


def create_sensor_support_j1_column():
    with model("sensor_support_j1_column") as ctx:
        column1 = cylinder(col_r + (tolerance / 2), 10, "column1") | place(0, 0, 7.5)
        column2 = cylinder(col_r + 4, 15, "column2")
        h_column3 = cylinder(col_r, 15, "column3") | place(0, 0, -5)

        column = union([column1, column2])
        column = difference(column, [h_column3])

        output(column)
    return ctx.graph


def create_base_cam():
    with model("base_cam") as ctx:
        base_cam = cube(50, 50, 10, "base_cam")

        h_nonslip_1 = cylinder(4, 6, "h_nonslip") | place(18, 18, -4)
        h_nonslip_2 = cylinder(4, 6, "h_nonslip") | place(-18, 18, -4)
        h_nonslip_3 = cylinder(4, 6, "h_nonslip") | place(18, -18, -4)
        h_nonslip_4 = cylinder(4, 6, "h_nonslip") | place(-18, -18, -4)

        base_colum_1 = cube(14, 14, 20, "base_columns") | place(18, 15, 12)
        h_column_1 = cylinder(
            col_r, 13, "column3"
        ) | rotate(90, 0, 90) | place(19, 15, 16)
        base_colum_1 = difference(base_colum_1, [h_column_1])

        base_colum_2 = base_colum_1 | translate(0, -30, 0)

        h_screw_1 = cylinder(4, 30, "h_screw")
        h_screw_2 = cylinder(8, 6, "h_screw") | place(0, 0, -2)

        h_light = cube(21, 50, 10, "h_light") | place(0, 0, 8)

        base_cam = difference(base_cam, [
            h_nonslip_1, h_nonslip_2, h_nonslip_3, h_nonslip_4,
            h_screw_1, h_screw_2, h_light,
        ])
        base_cam = union([base_cam, base_colum_1, base_colum_2])

        output(base_cam)
    return ctx.graph


def create_cover():
    with model("cover") as ctx:
        base_1 = cube(sqr_x * 2, 5, 10, "base") | place(0, sqr_y, 0)
        base_2 = cube(sqr_x * 2, 5, 10, "base") | place(0, -sqr_y, 0)
        base_3 = cube(5, sqr_y * 2, 10, "base") | place(sqr_x, 0, 0)
        base_4 = cube(5, sqr_y * 2, 10, "base") | place(-sqr_x, 0, 0)

        column1 = cylinder(col_r + 2, 10, "column1") | place(sqr_x, sqr_y, 0)
        column2 = cylinder(col_r + 2, 10, "column2") | place(-sqr_x, sqr_y, 0)
        column3 = cylinder(col_r + 2, 10, "column3") | place(sqr_x, -sqr_y, 0)
        column4 = cylinder(col_r + 2, 10, "column4") | place(-sqr_x, -sqr_y, 0)

        h_column1 = cylinder(col_r, 10, "column1") | place(sqr_x, sqr_y, 2)
        h_column2 = cylinder(col_r, 10, "column2") | place(-sqr_x, sqr_y, 2)
        h_column3 = cylinder(col_r, 10, "column3") | place(sqr_x, -sqr_y, 2)
        h_column4 = cylinder(col_r, 10, "column4") | place(-sqr_x, -sqr_y, 2)

        cover = union([
            base_1, base_2, base_3, base_4,
            column1, column2, column3, column4,
        ])
        cover = difference(cover, [h_column1, h_column2, h_column3, h_column4])

        t_cover = cover | translate(0, 0, 40)

        output(t_cover)
    return ctx.graph


def create_film_slider():
    with model("film_slider") as ctx:
        slider_base = cube(
            (sqr_x + 10) * 2, (sqr_x + 10) * 2, 5, "slider_base"
        )

        h_slider_1 = cube(40, 34.5, 30, "h_slider")
        h_slider_2 = cube(160, 35 + tolerance, 0.5, "h_slider") | place(0, 0, -2.25)
        h_slider_3 = cube(5, 34.5, 30, "h_slider") | rotate(0, 60, 0) | place(-25, 0, -2.25)

        h_column1 = cylinder(col_r + tolerance, 20, "column1") | place(sqr_x, sqr_y, 2)
        h_column2 = cylinder(col_r + tolerance, 20, "column2") | place(-sqr_x, sqr_y, 2)
        h_column3 = cylinder(col_r + tolerance, 20, "column3") | place(sqr_x, -sqr_y, 2)
        h_column4 = cylinder(col_r + tolerance, 20, "column4") | place(-sqr_x, -sqr_y, 2)

        join_1 = cube(40, 3, 3, "join_1") | place(0, 20, -4)
        join_2 = cube(40, 3, 3, "join_1") | place(0, -20, -4)

        slider = difference(slider_base, [
            h_slider_1, h_slider_2, h_slider_3,
            h_column1, h_column2, h_column3, h_column4,
        ])
        slider = union([slider, join_1, join_2])

        output(slider)
    return ctx.graph


def create_film_slider_2():
    with model("film_slider_2") as ctx:
        slider = cube(100, 45, 5, "slider") | place(0, 0, -5)
        h_slider_1 = cube(40, 34.5, 30, "h_slider")
        h_sprocket_gear = cube(15, 5, 10, "h_sprocket_gear")
        h_sprocket_gear_1 = h_sprocket_gear | place(30, 28.169/2, -5)
        h_sprocket_gear_2 = h_sprocket_gear | place(30, -28.169/2, -5)
        h_sprocket_col = cylinder(4, 60, "h_sprocket_col") | rotate(90, 0, 0) | place(30, 0, -7.5)

        sprocket_col_base_1 = cylinder(4.5, 3, "h_sprocket_col_base_1", 10) | rotate(90, 0, 0) | place(30, 28.169/2 + 6.9155, -7.5)
        sprocket_col_base_2 = cylinder(4.5, 3, "h_sprocket_col_base_2", 10) | rotate(90, 0, 0) | place(30, -28.169/2 - 6.9155, -7.5)
        h_sprocket_col_base = cylinder(2.25, 43, "h_sprocket_col_base") | rotate(90, 0, 0) | place(30, 0, -7.5)
        sprocket_col_base = union([sprocket_col_base_1, sprocket_col_base_2])
        sprocket_col_base = difference(sprocket_col_base, [h_sprocket_col_base])


        h_join_1 = cube(
            40 + tolerance, 3 + tolerance, 3 + tolerance, "join_1"
        ) | place(0, 20, -4)
        h_join_2 = cube(
            40 + tolerance, 3 + tolerance, 3 + tolerance, "join_1"
        ) | place(0, -20, -4)

        slider = difference(slider, [h_slider_1, h_join_1, h_join_2, h_sprocket_gear_1, h_sprocket_gear_2, h_sprocket_col])
        slider = union([slider, sprocket_col_base])

        output(slider)
    return ctx.graph

def create_sprocket_gear():
    with model("sprocket_gear") as ctx:
        col = cylinder(3, 16, "sprocket_gear", 10)  | rotate(90, 0, 0)  | place(30, 0, -7.5)
        film_cog = cylinder(4, 4, "film_cog") | rotate(90, 0, 0) | place(30, 6, -7.5)
        teeth = cube(1.5, 11, 1.5, "teeth")
        tooth = [
            teeth | rotate(0, 0, 360 / 8 * 1) ,
            teeth | rotate(0, 0, 360 / 8 * 2) ,
            teeth | rotate(0, 0, 360 / 8 * 3) ,
            teeth | rotate(0, 0, 360 / 8 * 4) ,
        ]

        tooth = union(tooth) | rotate(90, 0, 0) | place(30, 6, -7.5)

        sprocket_gear = union([col, film_cog, tooth])
        sprocket_gear = sprocket_gear | place(0, 8, 0)
        h_base_top =  cylinder(2, 5, "h_sprocket_col_base", 10) | rotate(90, 0, 0) | place(30, 2.5, -7.5)
        h_base_bottom =  cylinder(2, 5, "h_sprocket_col_base", 256) | rotate(90, 0, 0) | place(30, 13.5, -7.5)
        sprocket_gear = difference(sprocket_gear, [h_base_top, h_base_bottom])

        join_1 =  cylinder(2 - tolerance, 10 - tolerance * 2, "h_sprocket_col_base", 10) | rotate(90, 0, 0) | place(30, 0, -7.5)
        join_2 =  cylinder(2 - tolerance, 10.5 - tolerance * 2, "h_sprocket_col_base", 256) | rotate(90, 0, 0) | place(30, 16.25, -7.5)

        sprocket_gear = join([sprocket_gear, join_1, join_2])

        output(sprocket_gear)
    return ctx.graph

def create_dummy_film():
    with model("dummy_film") as ctx:
        d_x_sprockets = 4.7498
        d_y_sprockets = 28.169

        film_35mm = cube(200, 34.95, 0.3, "film_35mm")
        h_sprocket = cube(1.98, 2.98, 5, "h_sprocket")

        n = int((200 / 2) / d_x_sprockets)
        positions = [
            (d_x_sprockets * i, d_y_sprockets / 2, 0)
            for i in range(-n, n + 1)
        ] + [
            (d_x_sprockets * i, -d_y_sprockets / 2, 0)
            for i in range(-n, n + 1)
        ]

        h_sprockets_top = clones(h_sprocket, positions)
        h_sprockets_bottom = clones(h_sprocket, [(x, -y, z) for (x, y, z) in positions])
        film_35mm = difference(film_35mm, [h_sprockets_top, h_sprockets_bottom]) | place(0, 0, -2)

        output(film_35mm)
    return ctx.graph

# ---------------------------------------------------------------------------
# CLI: compile all parts to Blender scripts
# ---------------------------------------------------------------------------

ALL_PARTS = [
    # create_sensor_support,
    # create_lens_support,
    # create_columns,
    # create_film_support,
    # create_film_support_base,
    # create_film,
    # create_dummy_stepper,
    # create_motor_support,
    # create_h_motor_cog,
    # create_tol_cyl,
    # create_spacer,
    # create_cam_tripod_support,
    # create_sensor_support_j1,
    # create_sensor_support_j1_column,
    # create_base_cam,
    # create_cover,
    create_film_slider,
    create_film_slider_2,
    create_sprocket_gear,
    create_sensor_support_mark_ii,
    # create_dummy_film,
]

if __name__ == "__main__":
    import argparse
    from tanuki.dsl.export import combined_export, individual_export

    parser = argparse.ArgumentParser(description="Compile neganuki scanner parts")
    parser.add_argument(
        "--mode",
        choices=["combined", "individual"],
        default="combined",
        help="Export mode: combined (single file) or individual (one file per part)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file (combined) or directory (individual)",
    )
    args = parser.parse_args()

    if args.mode == "combined":
        out = args.output or "neganuki_scanner_gen.py"
        path = combined_export(ALL_PARTS, out)
        print(f"Generated {len(ALL_PARTS)} parts in {path} ({path.stat().st_size // 1024} KB)")
    else:
        out = args.output or "neganuki_scanner_gen"
        written = individual_export(ALL_PARTS, out)
        print(f"Generated {len(written)} files in {out}/")

