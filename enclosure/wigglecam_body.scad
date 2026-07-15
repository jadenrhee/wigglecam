// ============================================================================
// WiggleCam enclosure: parametric two-shell camera body
//
// Styled like a classic wide compact camera:
//   * raised top/bottom plates with a recessed "leatherette" mid band
//   * 4 lens holes in a horizontal row, each with a raised bezel ring
//   * flash window embedded in the top plate, engraved WIGGLECAM branding
//   * hand-grip bulge on the photographer's right, shutter button on top
// Back shell: raised screen bezel + cutout and mounting bosses for the
//   4.3" DSI touchscreen, vents, USB-C charge slot, tripod nut pocket.
// Shells join with 6x M3 screws into heat-set brass inserts.
//
// PART = "assembly" shows the closed camera standing upright (preview only).
// Set PART to "front" or "back", press F6, then File > Export STL to print.
// Every dimension is verified against the delivered parts with calipers
// before printing; vendor drawings drift between revisions.
// ============================================================================

PART    = "assembly";  // "front" | "back" | "assembly"
EXPLODE = 0;           // mm gap between shells in the assembly view

// ---- global body ----------------------------------------------------------
body_w   = 205;        // overall width  (sets the ~120 mm lens baseline)
body_h   = 92;         // overall height
body_d   = 54;         // overall depth (front+back shells)
wall     = 3;          // shell wall thickness (>=3 for rigidity)
corner_r = 8;          // outer corner radius
front_d  = 22;         // depth of front shell
back_d   = body_d - front_d;

// ---- camera-look cosmetics --------------------------------------------------
plate_h  = 16;         // top-plate band height on the front face
plate_t  = 2.5;        // how proud the top/bottom plates sit
base_h   = 12;         // bottom-plate band height
bezel_d  = 22;         // lens bezel ring outer diameter
bezel_h  = 4;          // bezel protrusion from the face
grip_w   = 26;         // grip bulge width
grip_d   = 9;          // grip protrusion from the face
grip_x   = body_w/2 - grip_w/2 - 2;
frame_t  = 2;          // screen bezel frame protrusion (back shell)

// ---- camera modules (Arducam quad kit, 25 x 25 mm boards) -----------------
cam_count      = 4;
cam_baseline   = 120;   // outermost lens centre-to-centre distance
cam_pitch      = cam_baseline / (cam_count - 1);   // 40 mm between lenses
cam_lens_d     = 16;    // clearance hole for the lens barrel
cam_board      = 25;    // module PCB is 25 x 25 mm
cam_hole_pitch = 21;    // M2 mounting holes, 21 x 21 mm pattern
cam_y          = 12;    // lens row height above body centreline

// ---- flash window (embedded in the top plate) -------------------------------
flash_w = 26;  flash_h = 9;           // diffuser window (print white PETG
flash_x = 0;   flash_y = body_h/2 - plate_h/2;   // insert or glue acrylic)

// ---- top-plate buttons (through the TOP wall) --------------------------------
// two 12 mm momentary switches: shutter (outer) + filter cycle (inner)
btn_d    = 13;                         // switch body + clearance
btn_xs   = [body_w/2 - 30, body_w/2 - 52];
btn_z    = front_d/2;                  // depth position on the top wall
collar_h = 2.5;                        // raised collar around each button

// ---- Raspberry Pi 5 + X1202 UPS stack --------------------------------------
pi_l = 85; pi_w = 56;
pi_hole_dx = 58; pi_hole_dy = 49;      // Pi mounting hole pattern
pi_boss_d = 7; pi_boss_h = 6;
stack_x = -30;                          // stack sits left of centre
stack_y = 0;

// ---- 4.3" DSI touchscreen (Waveshare), MEASURE THE ACTUAL PART --------------
scr_module_w = 122;  scr_module_h = 76;    // module outline
scr_view_w   = 106;  scr_view_h   = 63;    // visible area cutout
scr_hole_dx  = 114;  scr_hole_dy  = 68;    // M3 mounting pattern
scr_x = 18;  scr_y = 0;                    // position on back face

// ---- misc -------------------------------------------------------------------
usbc_w = 11; usbc_h = 6;               // charge-port slot to X1202 input
tripod_nut_af = 11.4;                  // 1/4-20 hex nut across-flats
screw_positions = [
    [ body_w/2-8,  body_h/2-8], [0,  body_h/2-8], [-body_w/2+8,  body_h/2-8],
    [ body_w/2-8, -body_h/2+8], [0, -body_h/2+8], [-body_w/2+8, -body_h/2+8]];
insert_d = 4.2; insert_h = 6;          // M3 heat-set insert pocket
$fn = 64;

// ============================================================================
// helpers
// ============================================================================
module body_outline() {                // rounded body cross-section, centred
    offset(corner_r) offset(-corner_r) square([body_w, body_h], center = true);
}

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

// raised band across the face (top/bottom plates), exterior side is z < 0
module face_band(y0, h) {
    translate([0, 0, -plate_t])
        linear_extrude(plate_t + 0.01)
            intersection() {
                body_outline();
                translate([-body_w/2 - 1, y0]) square([body_w + 2, h]);
            }
}

module lens_positions() {
    for (i = [0 : cam_count - 1])
        translate([-cam_baseline/2 + i*cam_pitch, cam_y, 0])
            children();
}

module lens_bezels() {                  // raised ring around each lens
    lens_positions() {
        translate([0, 0, -bezel_h]) cylinder(d = bezel_d, h = bezel_h + 0.01);
        translate([0, 0, -2]) cylinder(d1 = bezel_d, d2 = bezel_d + 3, h = 2.01);
    }
}

module lens_holes() {
    lens_positions() {
        translate([0, 0, -bezel_h - 1])
            cylinder(d = cam_lens_d, h = bezel_h + wall + 2);
        // shallow step in the bezel face, reads as a lens retaining ring
        translate([0, 0, -bezel_h - 1])
            cylinder(d = cam_lens_d + 3, h = 2);
    }
}

module grip() {                         // vertical bulge, photographer's right
    intersection() {
        hull()
            for (sy = [-1, 1])
                translate([grip_x, sy*(body_h/2 - 20), 0])
                    scale([1, 1, 2*grip_d/grip_w]) sphere(d = grip_w);
        translate([-body_w/2, -body_h/2, -grip_d - 1])
            cube([body_w, body_h, grip_d + 1]);   // keep the front half only
    }
}

module cam_bosses() {                   // M2 standoffs behind each lens hole
    lens_positions()
        translate([0, 0, wall])
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
            face_band(body_h/2 - plate_h, plate_h);   // top plate
            face_band(-body_h/2, base_h);             // bottom plate
            lens_bezels();
            grip();
            // button collars on the top wall
            for (bx = btn_xs)
                translate([bx, body_h/2 - 0.01, btn_z])
                    rotate([-90, 0, 0]) cylinder(d = btn_d + 7, h = collar_h);
        }
        lens_holes();
        // flash window through top plate + wall
        translate([flash_x - flash_w/2, flash_y - flash_h/2, -plate_t - 1])
            cube([flash_w, flash_h, plate_t + wall + 2]);
        // button holes down through collar + top wall
        for (bx = btn_xs)
            translate([bx, body_h/2 + collar_h + 1, btn_z])
                rotate([90, 0, 0]) cylinder(d = btn_d, h = wall + collar_h + 2);
        // branding engraved in the top plate (mirrored: face is viewed from -z)
        translate([-60, flash_y, -plate_t - 1])
            mirror([1, 0, 0])
                linear_extrude(2)
                    text("WIGGLECAM", size = 6, halign = "center",
                         valign = "center",
                         font = "Liberation Sans:style=Bold");
    }
    cam_bosses();
    pi_bosses();
    screw_bosses(front_d);
}

module back_shell() {
    difference() {
        union() {
            shell(back_d);
            // raised screen bezel frame
            translate([scr_x, scr_y, -frame_t])
                linear_extrude(frame_t + 0.01)
                    offset(5) offset(-5)
                        square([scr_view_w + 14, scr_view_h + 14], center = true);
        }
        // screen viewing window through frame + wall
        translate([scr_x - scr_view_w/2, scr_y - scr_view_h/2, -frame_t - 1])
            cube([scr_view_w, scr_view_h, frame_t + wall + 2]);
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
        translate([scr_x + sx*scr_hole_dx/2, scr_y + sy*scr_hole_dy/2, wall])
            difference() {
                cylinder(d = 7, h = 5);
                translate([0, 0, 1]) cylinder(d = 2.4, h = 5);
            }
    screw_bosses(back_d);
}

// ============================================================================
// assembly preview (never exported; set PART to "front"/"back" for STLs)
// ============================================================================
module place_back() {                   // fold the back shell onto the front
    translate([0, 0, body_d + EXPLODE]) rotate([0, 180, 0]) children();
}

module assembly_mockups() {             // dummy hardware so the preview reads
    lens_positions() {                  // lens barrels + glass
        color([0.08, 0.08, 0.09])
            translate([0, 0, -bezel_h - 2]) cylinder(d = 15, h = bezel_h + 6);
        color([0.15, 0.20, 0.45])
            translate([0, 0, -bezel_h - 2.7]) cylinder(d = 10, h = 0.8);
    }
    color([0.96, 0.95, 0.88])           // flash diffuser
        translate([flash_x - (flash_w - 0.6)/2, flash_y - (flash_h - 0.6)/2,
                   -plate_t + 0.4])
            cube([flash_w - 0.6, flash_h - 0.6, plate_t + wall - 1]);
    color([0.75, 0.15, 0.15])           // shutter button cap (outer)
        translate([btn_xs[0], body_h/2 + 0.5, btn_z])
            rotate([-90, 0, 0]) cylinder(d = btn_d - 1.5, h = collar_h + 1.5);
    color([0.35, 0.35, 0.38])           // filter button cap (inner)
        translate([btn_xs[1], body_h/2 + 0.5, btn_z])
            rotate([-90, 0, 0]) cylinder(d = btn_d - 1.5, h = collar_h + 1.5);
    place_back()                        // screen glass
        color([0.05, 0.05, 0.08])
            translate([scr_x - scr_view_w/2, scr_y - scr_view_h/2, -frame_t + 0.4])
                cube([scr_view_w, scr_view_h, frame_t]);
}

if (PART == "front") front_shell();
if (PART == "back")  back_shell();
if (PART == "assembly")
    rotate([90, 0, 0]) {                // stand the camera upright for preview
        color([0.24, 0.24, 0.26]) front_shell();
        color([0.18, 0.18, 0.20]) place_back() back_shell();
        assembly_mockups();
    }
