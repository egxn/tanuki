"""Example gear set for small DC/stepper motor drive trains.

All gears follow the ISO module system (module = pitch_diameter / n_teeth).

Drive-train configurations included
────────────────────────────────────
1. Motor pinion (9T, m1)          — press-fit on a 3 mm D-shaft (hex)
2. Reduction stage 1 (9T → 36T)  — 4:1 first stage, m1, round axle
3. Reduction stage 2 (9T → 45T)  — 5:1 second stage, m0.8, round axle
4. Idler gear (20T, m1)           — reverses rotation direction between shafts
5. Helical drive pair (20T/40T)   — smooth, low-noise, typical for gearboxes
6. Compound gear (36T / 9T)       — two-stage co-axial; stage 1 output + stage 2 input

Module / tooth combinations follow standard sizes for small motors:
  m0.5  — micro-servo range (⌀ ≤ 10 mm gears common)
  m0.8  — mini motors, RC servos, watch mechanisms
  m1    — N20 / N30 / 130-size DC motors, NEMA-17 steppers
  m1.5  — NEMA-23 steppers, small CNC drives

Print notes
-----------
Material   : PLA / PETG for low load; ABS / PA12 for high torque
Orientation: flat (XY plane), no supports required
Infill     : 50–80 %, rectilinear
Perimeters : ≥ 4
Layer      : 0.10–0.15 mm (m ≤ 1), 0.15–0.20 mm (m ≥ 1.5)
"""

from tanuki.dsl import join, model, output
from tanuki.mori.print_labo.utils import (
    spur_gear,
    spur_gear_pair,
    helical_gear,
    hex_hole,
)
from tanuki.dsl import difference

# ── Shared tolerance ─────────────────────────────────────────────────────────
TOL = 0.1   # mm — radial clearance; gives light backlash for 3-D-printed gears


# ── 1. Motor pinion — N20 / N30 motor (m1, 9T, D-shaft 3 mm) ──────────────

def create_motor_pinion():
    """9-tooth m1 pinion for a D-shaft N20/N30 micro motor.

    Hex hole approximates a D-shaft: a 3 mm hex across-flats gives a
    press-fit on the motor spindle while preventing rotation.

    Specs: m=1, N=9, PD=9 mm, OD≈11 mm, face=8 mm
    """
    with model("motor_pinion") as ctx:
        output(spur_gear(
            module=1.0, n_teeth=9, width=8.0,
            hex_flats=3.0, hex_tolerance=0.05,
            sharpness=3.5,
            tolerance=TOL,
            label="motor_pinion",
        ))
    return ctx.graph


# ── 2. First reduction stage — 4:1 (9T drive → 36T driven, m1) ───────────

def create_reduction_stage1_pair():
    """4:1 reduction pair for a typical N20 motor gearbox first stage.

    Pinion (9T) on motor shaft, driven gear (36T) on intermediate shaft.
    Centre distance = (9 + 36) / 2 × 1 = 22.5 mm.

    Specs: m=1, ratio=4:1, face=8 mm, axle holes 3 mm / 5 mm
    """
    with model("reduction_stage1") as ctx:
        pinion, driven = spur_gear_pair(
            module=1.0, n_teeth_a=9, n_teeth_b=36, width=8.0,
            hole_d_a=3.0, hole_d_b=5.0,
            sharpness=3.5, tolerance=TOL,
            label="stage1",
        )
        output(join([pinion, driven]))
    return ctx.graph


# ── 3. Second reduction stage — 5:1 (9T drive → 45T driven, m0.8) ────────

def create_reduction_stage2_pair():
    """5:1 reduction second stage for a two-speed gearbox (m0.8).

    Smaller module allows a more compact stage while keeping enough tooth
    count for adequate strength.
    Centre distance = (9 + 45) / 2 × 0.8 = 21.6 mm.

    Specs: m=0.8, ratio=5:1, face=6 mm, axle holes 3 mm / 5 mm
    """
    with model("reduction_stage2") as ctx:
        pinion, driven = spur_gear_pair(
            module=0.8, n_teeth_a=9, n_teeth_b=45, width=6.0,
            hole_d_a=3.0, hole_d_b=5.0,
            sharpness=3.5, tolerance=TOL,
            label="stage2",
        )
        output(join([pinion, driven]))
    return ctx.graph


# ── 4. Idler gear — direction reversal (20T, m1) ─────────────────────────

def create_idler():
    """20-tooth m1 idler that reverses rotation between two parallel shafts.

    An idler gear meshes between a driver and a driven gear to keep them
    rotating in the same direction (without changing the ratio).  A small
    axle hole (5 mm) fits a standard M5 standoff or shoulder bolt.

    Specs: m=1, N=20, PD=20 mm, OD≈22 mm, face=8 mm
    """
    with model("idler_gear") as ctx:
        output(spur_gear(
            module=1.0, n_teeth=20, width=8.0,
            hole_d=5.0,
            sharpness=3.5, tolerance=TOL,
            label="idler",
        ))
    return ctx.graph


# ── 5. Helical drive pair — quiet/high-load 2:1 (20T/40T, m1.5, 20°) ─────

def create_helical_pair():
    """2:1 helical gear pair for quiet, smooth operation.

    Helical gears have a gradual tooth engagement that distributes load across
    multiple teeth simultaneously.  Common in small CNC spindles, extruder
    drives and camera focus mechanisms.

    Gears use opposite helix directions (+1 / -1).
    Centre distance = (20 + 40) / 2 × 1.5 = 45 mm.

    Specs: m=1.5, ratio=2:1, face=15 mm, helix=20°, axle 5 mm / 8 mm
    """
    with model("helical_pair") as ctx:
        gear_a = helical_gear(
            module=1.5, n_teeth=20, width=15.0,
            helix_angle_deg=20.0, helix_direction=1,
            hole_d=5.0, sharpness=3.5, tolerance=TOL,
            label="helical_driver",
        )
        gear_b = helical_gear(
            module=1.5, n_teeth=40, width=15.0,
            helix_angle_deg=20.0, helix_direction=-1,
            hole_d=8.0, sharpness=3.5, tolerance=TOL,
            label="helical_driven",
        )
        # Position driven gear at correct centre distance (along Y)
        from tanuki.dsl import translate
        centre = 1.5 * (20 + 40) / 2
        half_pitch = 180.0 / 40
        from tanuki.dsl import rotate
        gear_b_placed = gear_b | translate(0, centre, 0) | rotate(0, 0, half_pitch)
        output(join([gear_a, gear_b_placed]))
    return ctx.graph


# ── 6. Compound gear — 36T outer / 9T inner (m1) ─────────────────────────

def create_compound_gear():
    """Co-axial compound gear: 36T (input) + 9T (output) on same shaft.

    Compound gears stack a large driven gear and a small driving gear on a
    single shared axle.  Each stage multiplies the overall reduction.
    With a 9→36 first stage and this 36→9 second stage, a full two-stage
    reduction gives 4 × 4 = 16:1 (assuming a matching driven gear downstream).

    The 36T is 8 mm wide, the 9T pinion is 8 mm wide, offset by face width.
    A 5 mm hex hole (M5 nut) locks both wheels to the shaft.

    Specs: m=1, 36T+9T co-axial, total height=16 mm, hex 5.5 mm (M3 nut → no)
           — here using 8 mm hex for M5 nut, which tolerates the torque well.
    """
    with model("compound_gear") as ctx:
        from tanuki.dsl import translate

        large = spur_gear(
            module=1.0, n_teeth=36, width=8.0,
            hex_flats=8.0, hex_tolerance=0.1,
            sharpness=3.5, tolerance=TOL,
            label="compound_large",
        )
        small = (
            spur_gear(
                module=1.0, n_teeth=9, width=8.0,
                hex_flats=8.0, hex_tolerance=0.1,
                sharpness=3.5, tolerance=TOL,
                label="compound_small",
            )
            | translate(0, 0, 8.0)   # stack axially on top of the large gear
        )
        output(join([large, small]))
    return ctx.graph


# ── Part registry ─────────────────────────────────────────────────────────────

ALL_PARTS = [
    create_motor_pinion,
    create_reduction_stage1_pair,
    create_reduction_stage2_pair,
    create_idler,
    create_helical_pair,
    create_compound_gear,
]


if __name__ == "__main__":
    import argparse
    from tanuki.dsl.export import combined_export, individual_export

    parser = argparse.ArgumentParser(description="Compile motor_gears parts")
    parser.add_argument(
        "--mode", choices=["combined", "individual"], default="combined"
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.mode == "combined":
        out = args.output or "motor_gears_gen.py"
        path = combined_export(ALL_PARTS, out)
        print(f"Generated {len(ALL_PARTS)} parts → {path}")
    else:
        out = args.output or "motor_gears_gen"
        written = individual_export(ALL_PARTS, out)
        print(f"Generated {len(written)} files → {out}/")
