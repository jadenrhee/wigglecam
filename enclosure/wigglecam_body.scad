// ============================================================================
// WiggleCam enclosure — parametric two-shell camera body
//
// Front shell: 4 lens openings in a horizontal row, flash window,
//              shutter button hole, hand grip bulge.
// Back shell:  cutout + mounting bosses for the 4.3" DSI touchscreen,
//              vents, USB-C charge port slot, tripod nut pocket.
// Shells join with 6x M3 screws into heat-set brass inserts.
//
// Render either shell by setting PART below, then File > Export STL.
// Verify every *_actual dimension against your delivered parts with
// calipers before printing — vendor drawings drift between revisions.
// ============================================================================

PART = "front";        // "front" | "back" | "assembly"

// ---- global body ----------------------------------------------------------
body_w   = 205;        // overall width  (sets the ~120 mm lens baseline)
body_h   = 92;         // overall height
body_d   = 54;         // overall depth (front+back shells)
wall     = 3;          // shell wall thickness (>=3 for rigidity)
corner_r = 8;          // outer corner radius
front_d  = 22;         // depth of front shell
back_d   = body_d - front_d;

// ---- camera modules (Arducam quad kit, 25 x 25 mm boards) -----------------
cam_count      = 4;
cam_baseline   = 120;   // outermost lens centre-to-centre distance
cam_pitch      = cam_baseline / (cam_count - 1);   // 40 mm between lenses
cam_lens_d     = 16;    // clearance hole for the lens barrel
cam_board      = 25;    // module PCB is 25 x 25 mm
cam_hole_pitch = 21;    // M2 mounting holes, 21 x 21 mm pattern
cam_z          = 12;    // lens row height above body centreline

// ---- flash window ----------------------------------------------------------
flash_w = 30;  flash_h = 14;          // diffuser window (print white PETG
flash_x = 0;   flash_z = -26;         // insert or glue acrylic behind it)

// ---- shutter button ---------------------------------------------------------
btn_d = 13;                            // 12 mm momentary switch + clearance
btn_x = body_w/2 - 24;                 // top-right, index-finger position
btn_from_top = 16;

// ---- Raspberry Pi 5 + X1202 UPS stack --------------------------------------
pi_l = 85; pi_w = 56;
pi_hole_dx = 58; pi_hole_dy = 49;      // Pi mounting hole pattern
pi_boss_d = 7; pi_boss_h = 6;
stack_x = -30;                          // stack sits left of centre
stack_y = 0;

// ---- 4.3" DSI touchscreen (Waveshare) — MEASURE YOURS -----------------------
scr_module_w = 122;  scr_module_h = 76;    // module outline
scr_view_w   = 106;  scr_view_h   = 63;    // visible area cutout
scr_hole_dx  = 114;  scr_hole_dy  = 68;    // M3 mounting pattern
scr_x = 18;  scr_z = 0;                    // position on back face

// ---- misc -------------------------------------------------------------------
usbc_w = 11; usbc_h = 6;               // charge-port slot to X1202 input
tripod_nut_af = 11.4;                  // 1/4-20 hex nut across-flats
screw_positions = [
    [ body_w/2-8,  body_h/2-8], [0,  body_h/2-8], [-body_w/2+8,  body_h/2-8],
    [ body_w/2-8, -body_h/2+8], [0, -body_h/2+8], [-body_w/2+8, -body_h/2+8]];
insert_d = 4.2; insert_h = 6;          // M3 heat-set insert pocket
$fn = 48;

// ============================================================================
// helpers
// ============================================================================
module rbox(w, h, d, r) {              // rounded-corner box, centred in XY
    linear_extrude(d)
        offset(r) offset(-r) square([w, h], center = true);
}

module shell(depth) {                   // one hollow half-shell
    difference() {
        rbox(body_w, body_h, depth, corner_r);
        translate([0, 0, wall])
            rbox(body_w - 2*wall, body_h - 2*wall, depth, corner_r - wall);
    }
}

module lens_holes() {
    for (i = [0 : cam_count - 1])
        translate([-cam_baseline/2 + i*cam_pitch, cam_z, -1])
            cylinder(d = cam_lens_d, h = wall + 2);
}

module cam_bosses() {                   // M2 standoffs behind each lens hole
    for (i = [0 : cam_count - 1])
        translate([-cam_baseline/2 + i*cam_pitch, cam_z, wall])
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx*cam_hole_pitch/2, sy*cam_hole_pitch/2, 0])
                    difference() {
                        cylinder(d = 5, h = 4);
                        translate([0, 0, 1]) cylinder(d = 1.6, h = 4);
                    }
}

module pi_bosses() {
    translate([stack_x, stack_y, wall])
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*pi_hole_dx/2, sy*pi_hole_dy/2, 0])
                difference() {
                    cylinder(d = pi_boss_d, h = pi_boss_h);
                    translate([0, 0, 1]) cylinder(d = 2.4, h = pi_boss_h);
                }
}

module screw_bosses(depth) {
    for (p = screw_positions)
        translate([p[0], p[1], wall])
            difference() {
                cylinder(d = insert_d + 4, h = depth - wall);
                translate([0, 0, depth - wall - insert_h])
                    cylinder(d = insert_d, h = insert_h + 1);
            }
}

module vents(x0) {
    for (i = [0:5])
        translate([x0 + i*7, -body_h/2 - 1, back_d - 14])
            cube([3.5, wall + 2, 9]);
}

// ============================================================================
// parts
// ============================================================================
module front_shell() {
    difference() {
        union() {
            shell(front_d);
            // grip bulge on the right edge
            translate([body_w/2 - 6, 0, 0])
                scale([0.5, 1, 1])
                    cylinder(d = 34, h = front_d);
        }
        lens_holes();
        translate([flash_x - flash_w/2, flash_z - flash_h/2, -1])
            cube([flash_w, flash_h, wall + 2]);
        translate([btn_x, body_h/2 - btn_from_top, -1])
            cylinder(d = btn_d, h = wall + 2);
    }
    cam_bosses();
    pi_bosses();
    screw_bosses(front_d);
}

module back_shell() {
    difference() {
        shell(back_d);
        // screen viewing window
        translate([scr_x - scr_view_w/2, scr_z - scr_view_h/2, -1])
            cube([scr_view_w, scr_view_h, wall + 2]);
        // USB-C charge slot (left side wall, feeds the X1202 input)
        translate([-body_w/2 - 1, -usbc_w/2, back_d - 14])
            cube([wall + 2, usbc_w, usbc_h]);
        vents(-body_w/2 + 20);
        // tripod nut pocket, bottom centre
        translate([0, -body_h/2 + wall/2, back_d/2])
            rotate([90, 0, 0])
                cylinder(d = tripod_nut_af / cos(30), h = wall + 1, $fn = 6);
        translate([0, -body_h/2 - 1, back_d/2])
            rotate([-90, 0, 0])
                cylinder(d = 6.8, h = wall + 2);   // 1/4" bolt clearance
    }
    // screen mounting bosses
    for (sx = [-1, 1], sy = [-1, 1])
        translate([scr_x + sx*scr_hole_dx/2, scr_z + sy*scr_hole_dy/2, wall])
            difference() {
                cylinder(d = 7, h = 5);
                translate([0, 0, 1]) cylinder(d = 2.4, h = 5);
            }
    screw_bosses(back_d);
}

// ============================================================================
if (PART == "front")     front_shell();
if (PART == "back")      back_shell();
if (PART == "assembly") { front_shell();
    translate([0, 0, body_d + 10]) rotate([0, 180, 0]) back_shell(); }
