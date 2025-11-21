from util.line import Line
from util.pattern_piece import PatternPiece
import math
from util.measurements import Measurements
from util.garment_specs import GarmentSpecs
from util.dart import Dart

DART_ROTATION_THRESHOLD = 1.0 # Inches of waist suppression below which darts are combined

def draft(measurements, garment_specs):
    """
    Drafts a two-dart bodice block based on provided measurements.
    """
    pattern_pieces = []

    # --- DRAFT FRONT BODICE ---
    front_lines = []
    front_body_lines = []
    front_drafting_lines = []
    front_marking_lines = []
    
    # Basic measurements with ease
    bust_circ = measurements.bust + garment_specs.bust_ease
    waist_circ = measurements.waist + garment_specs.waist_ease
    
    # Foundational lines
    # Add extra length to the front to accommodate the bust.
    # TODO: This should ideally be based on a direct front-waist measurement.
    bust_projection_difference = measurements.shoulder_to_bust - measurements.back_bust_height
    center_front_y = measurements.shoulder_to_waist + bust_projection_difference

    front_width = measurements.front_bust / 2 + garment_specs.bust_ease / 2
    
    # Calculate neckline width based on neck circumference
    neck_width = measurements.neck_circumference / (2 * math.pi)
    side_neck_rise = measurements.side_neck_rise

    # Use the GarmentSpecs to create the neckline
    front_neckline, neckline_edge = garment_specs.create_bodice_neckline("Front", side_neck_rise)
    # Center Front Line
    front_neck_depth = garment_specs.front_neckline_depth
    front_lines.append(Line.vertical(0, front_neck_depth, center_front_y))
    front_lines.append(front_neckline)

    # Shoulder
    shoulder_slope_drop = side_neck_rise + measurements.shoulder_slope
    shoulder_point_x = neck_width + measurements.shoulder_length
    shoulder_point = (shoulder_point_x, shoulder_slope_drop)
    front_lines.append(Line([(neckline_edge, side_neck_rise), (shoulder_point_x, shoulder_slope_drop)]))

    # Armscye
    armscye_depth = measurements.shoulder_to_armpit - 1
    across_chest = measurements.across_front / 2
    armscye_guide_y = armscye_depth / 2

    # Add drafting lines for reference points
    front_drafting_lines.append(Line.horizontal(armscye_depth, 0, front_width))
    front_drafting_lines.append(Line.vertical(across_chest, 0, center_front_y))
    front_drafting_lines.append(Line.vertical(front_width, 0, center_front_y))
    front_body_lines.append(Line.horizontal(armscye_guide_y, 0, across_chest))
    
    # The top of the armscye is a straight line perpendicular to the shoulder seam.
    # TODO: The length of this straight part could be a specific measurement.
    armscye_straight_len = armscye_depth / 5
    shoulder_line_front = Line([(neckline_edge, side_neck_rise), shoulder_point])
    curve_start_point = shoulder_line_front.get_perpendicular_point(shoulder_point, armscye_straight_len)

    # The third guide point is on a 1-inch diagonal from the chest/armscye corner.
    # TODO: The 1-inch length could be a calculated proportion.
    diagonal_guide_len = 0.5
    guide_point_3 = (across_chest - diagonal_guide_len * math.cos(math.radians(45)), armscye_depth - diagonal_guide_len * math.sin(math.radians(45)))
    armscye_points = [shoulder_point, curve_start_point, guide_point_3, (front_width, armscye_depth)]
    front_lines.append(Line(armscye_points, smooth=True))

    # Calculate total waist suppression needed for the front
    total_front_waist_suppression = front_width - (waist_circ / 4)

    # Distribute 1/3 of the suppression to the side seam
    side_seam_suppression = total_front_waist_suppression / 3
    front_waist_x = front_width - side_seam_suppression

    # Side Seam
    side_seam_line = Line([(front_width, armscye_depth), (front_waist_x, center_front_y)])
    front_lines.append(side_seam_line)
    
    # Hem
    # The hemline should end exactly where it meets the side seam.
    # This should change to be curved in the future
    hem_end_x = side_seam_line.get_x_for_y(center_front_y)
    front_lines.append(Line.horizontal(center_front_y, 0, hem_end_x))

    # Darts
    bust_point_x = measurements.bust_point_separation / 2
    bust_point_y = measurements.shoulder_to_bust
    
    # Add bust apex cross mark
    apex_mark_size = 0.25
    apex_horizontal = [(bust_point_x - apex_mark_size, bust_point_y), (bust_point_x + apex_mark_size, bust_point_y)]
    apex_vertical = [(bust_point_x, bust_point_y - apex_mark_size), (bust_point_x, bust_point_y + apex_mark_size)]
    front_marking_lines.extend([Line(apex_horizontal), Line(apex_vertical)])

    front_body_lines.append(Line.horizontal(bust_point_y, 0, front_width))

    # Back the dart tip off from the bust apex for a better fit.
    # We'll back it off by 20% of the distance from the apex to the side seam.
    dart_back_off = (front_width - bust_point_x) * 0.20
    dart_tip_x = bust_point_x + dart_back_off
    
    # Bust Dart (from side seam)
    # The dart intake is determined by the extra length needed for the bust.
    # This is the difference between the front shoulder-to-bust and the back nape-to-bust measurements.
    bust_dart_intake = measurements.shoulder_to_bust - measurements.back_bust_height

    bust_dart_center_y = bust_point_y
    bust_dart_center_x = side_seam_line.get_x_for_y(bust_dart_center_y)
    bust_dart = Dart(side_seam_line, (bust_dart_center_x, bust_dart_center_y), bust_dart_intake, (dart_tip_x, bust_point_y), name="Bust Dart")
    if bust_dart and bust_dart.leg1:
        front_marking_lines.append(bust_dart)

    # Waist Dart
    # The remaining 2/3 of suppression goes into the vertical waist dart
    waist_dart_width = total_front_waist_suppression * (2/3)
    dart_center_x = bust_point_x
    dart_tip_y = bust_point_y + 1.5
    hem_line_for_dart = Line.horizontal(center_front_y, 0, front_waist_x)
    waist_dart = Dart(hem_line_for_dart, (dart_center_x, center_front_y), waist_dart_width, (dart_center_x, dart_tip_y), name="Front Waist Dart")
    if waist_dart and waist_dart.leg1:
        front_marking_lines.append(waist_dart)

    front_piece = PatternPiece(name="Front Bodice", body_lines=front_body_lines, pattern_lines=front_lines, drafting_lines=front_drafting_lines, marking_lines=front_marking_lines)
    front_piece.add_grainline()
    front_piece.add_seam_allowance(garment_specs.seam_allowance)
    pattern_pieces.append(front_piece)


    # --- DRAFT BACK BODICE ---
    back_lines = []
    back_drafting_lines = []
    back_body_lines = []
    back_marking_lines = []

    # Foundational lines
    center_back_y = measurements.shoulder_to_waist
    back_width = measurements.back_bust / 2 + garment_specs.bust_ease / 2

    # Use the GarmentSpecs to create the neckline
    back_neckline, neckline_edge = garment_specs.create_bodice_neckline("Back", side_neck_rise)
    # Center Back Line
    back_neck_depth = garment_specs.back_neckline_depth
    back_lines.append(Line.vertical(0, back_neck_depth, center_back_y))
    back_lines.append(back_neckline)

    # Armscye
    across_back = measurements.across_back / 2

    # Add drafting lines for reference points
    back_drafting_lines.append(Line.horizontal(armscye_depth, 0, back_width))
    back_drafting_lines.append(Line.vertical(across_back, 0, center_back_y))
    back_drafting_lines.append(Line.vertical(back_width, 0, center_back_y))
    back_body_lines.append(Line.horizontal(armscye_guide_y, 0, across_back))
    back_body_lines.append(Line.horizontal(measurements.back_bust_height, 0, back_width))

    # Calculate total waist suppression for the back
    total_back_waist_suppression = back_width - (waist_circ / 4)

    # Distribute 1/3 to the side seam
    back_side_seam_suppression = total_back_waist_suppression / 3
    back_waist_x = back_width - back_side_seam_suppression

    # Side Seam
    back_side_seam_line = Line([(back_width, armscye_depth), (back_waist_x, center_back_y)])
    back_lines.append(back_side_seam_line)

    # Hem
    back_hem_end_x = back_side_seam_line.get_x_for_y(center_back_y)
    back_lines.append(Line.horizontal(center_back_y, 0, back_hem_end_x))

    # --- Darts and Final Seams for Back ---
    shoulder_dart_intake = measurements.back_shoulder_length - measurements.shoulder_length

    if total_back_waist_suppression < DART_ROTATION_THRESHOLD:
        # If waist shaping is minimal, rotate the shoulder dart into the waist dart.
        print("Rotating back shoulder dart into waist dart.")
        # Draw the shoulder seam at its final (shorter) length.
        shoulder_line = Line([(neckline_edge, side_neck_rise), (neck_width + measurements.shoulder_length, shoulder_slope_drop)])
        
        # The waist dart now absorbs all suppression.
        back_waist_dart_width = total_back_waist_suppression + shoulder_dart_intake
    else:
        # If there's significant waist shaping, use both a shoulder and waist dart.
        # Draw the shoulder seam at its longer length to accommodate the dart.
        shoulder_line = Line([(neckline_edge, side_neck_rise), (neck_width + measurements.back_shoulder_length, shoulder_slope_drop)])
        
        # Create the shoulder dart.
        dart_length = measurements.nape_to_shoulder_blade
        shoulder_midpoint = shoulder_line.get_midpoint()
        shoulder_dart_tip = shoulder_line.get_perpendicular_point(shoulder_midpoint, dart_length)
        shoulder_dart = Dart(shoulder_line, shoulder_midpoint, shoulder_dart_intake, shoulder_dart_tip, name="Shoulder Dart")
        if shoulder_dart and shoulder_dart.leg1:
            back_marking_lines.append(shoulder_dart)
        
        # The waist dart takes the remaining 2/3 of waist suppression.
        back_waist_dart_width = total_back_waist_suppression * (2/3)

    back_lines.append(shoulder_line)
    shoulder_point_back = shoulder_line.points[-1]
    curve_start_point_back = shoulder_line.get_perpendicular_point(shoulder_point_back, armscye_straight_len)
    guide_point_3_back = (across_back - diagonal_guide_len * math.cos(math.radians(45)), armscye_depth - diagonal_guide_len * math.sin(math.radians(45)))
    back_armscye_points = [shoulder_point_back, curve_start_point_back, guide_point_3_back, (back_width, armscye_depth)]
    back_lines.append(Line(back_armscye_points, smooth=True))

    # Create the waist dart legs to be passed to the truing function
    back_dart_center_x = back_width / 2
    back_dart_tip_y = armscye_depth + 1
    back_hem_for_dart = Line.horizontal(center_back_y, 0, back_waist_x)
    back_waist_dart = Dart(back_hem_for_dart, (back_dart_center_x, center_back_y), back_waist_dart_width, (back_dart_center_x, back_dart_tip_y), name="Back Waist Dart")
    if back_waist_dart and back_waist_dart.leg1:
        back_marking_lines.append(back_waist_dart)

    back_piece = PatternPiece(name="Back Bodice", body_lines=back_body_lines, pattern_lines=back_lines, drafting_lines=back_drafting_lines, marking_lines=back_marking_lines)
    back_piece.add_grainline()
    back_piece.add_seam_allowance(garment_specs.seam_allowance)
    pattern_pieces.append(back_piece)

    # --- TRUE SIDE SEAMS ---
    # This is done after both pieces are drafted to ensure all lines are available.
    # The goal is to make the front side seam length match the back side seam length
    # when the front bust dart is closed.

    # 1. Get the back side seam line from the back piece and calculate its length.
    # It's the line connecting the armscye to the waist.
    back_side_seam = back_piece.pattern_lines[-4] # Based on current append order
    back_side_seam_length = math.dist(back_side_seam.points[0], back_side_seam.points[1])

    # 2. Get the front side seam and bust dart from the front piece.
    front_side_seam = front_piece.pattern_lines[-2]
    front_bust_dart = front_piece.get_marking_by_name("Bust Dart")
    if not front_bust_dart:
        print("Warning: Could not find front bust dart for truing side seams.")
        return pattern_pieces

    # 3. Calculate the "closed" length of the front side seam.
    side_seam_top_point = front_side_seam.points[0]
    side_seam_bottom_point = front_side_seam.points[1]
    dart_leg1_start = front_bust_dart.leg1.points[0]
    dart_leg2_start = front_bust_dart.leg2.points[0]

    # Ensure leg1 is the upper leg for clarity
    upper_dart_leg_start = dart_leg1_start if dart_leg1_start[1] < dart_leg2_start[1] else dart_leg2_start
    lower_dart_leg_start = dart_leg2_start if dart_leg1_start[1] < dart_leg2_start[1] else dart_leg1_start

    upper_seam_length = math.dist(side_seam_top_point, upper_dart_leg_start)
    lower_seam_length = math.dist(lower_dart_leg_start, side_seam_bottom_point)
    closed_front_seam_length = upper_seam_length + lower_seam_length

    # 4. Calculate the difference and adjust the front waist point.
    length_difference = closed_front_seam_length - back_side_seam_length
    adjusted_front_waist_y = side_seam_bottom_point[1] - length_difference

    # 5. Redefine the front side seam, hem, and waist dart with the adjusted point.
    front_side_seam.points[1] = (side_seam_bottom_point[0], adjusted_front_waist_y)
    
    front_hem = front_piece.pattern_lines[-1]
    front_hem.points = [(0, adjusted_front_waist_y), (front_side_seam.points[1][0], adjusted_front_waist_y)]

    front_waist_dart = front_piece.get_marking_by_name("Front Waist Dart")
    if not front_waist_dart:
        print("Warning: Could not find front waist dart for truing side seams.")
        return pattern_pieces
    front_waist_dart.seam_line.points = front_hem.points # Update the dart's seam line reference
    front_waist_dart.leg1.points[0] = (front_waist_dart.leg1.points[0][0], adjusted_front_waist_y)
    front_waist_dart.leg2.points[0] = (front_waist_dart.leg2.points[0][0], adjusted_front_waist_y)

    return pattern_pieces

if __name__ == "__main__":
    from util.draw import draw_pattern
    
    measurements = Measurements.from_file('patternDrafting/measurements/sample_measurements.yaml')
    garment_specs = GarmentSpecs.from_file('patternDrafting/garmentSpecs/sample_garment_specs.yaml')

    pattern_pieces = draft(measurements, garment_specs)
    
    draw_pattern(
        scale=100,
        pattern_pieces=pattern_pieces,
        seam_allowance=garment_specs.seam_allowance,
        output_filepath="testFiles/bodiceBlock.png",
        pattern_name="Bodice Block"
    )
