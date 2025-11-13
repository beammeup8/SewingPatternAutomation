from .line import Line
import math

def create_dart(seam_line, center_point_on_seam, dart_width, dart_tip):
    """
    Creates a dart along a given seam line.

    Args:
        seam_line (Line): The line (can be straight or curved) where the dart opens.
        center_point_on_seam (tuple): The (x, y) point on the seam line where the dart is centered.
        dart_width (float): The total width of the dart opening, measured along the seam.
        dart_tip (tuple): The (x, y) point of the dart's tip.

    Returns:
        list[Line]: A list containing the two Line objects for the dart legs.
    """
    # Find the two points on the seam line that define the dart opening.
    # This requires finding points along the curve at a certain distance.
    # For simplicity with straight lines, we can use linear interpolation.
    
    # This is a simplified approach for straight lines. A curved line would
    # require walking along the curve's points to measure arc length.
    if len(seam_line.points) == 2:
        p1_x, p1_y = seam_line.points[0]
        p2_x, p2_y = seam_line.points[1]

        # Determine the direction vector of the seam line
        line_length = math.dist((p1_x, p1_y), (p2_x, p2_y))
        if line_length == 0: return []
        
        vx = (p2_x - p1_x) / line_length
        vy = (p2_y - p1_y) / line_length

        # Calculate the positions of the dart legs on the seam line
        leg1_x = center_point_on_seam[0] - (dart_width / 2) * vx
        leg1_y = center_point_on_seam[1] - (dart_width / 2) * vy
        leg2_x = center_point_on_seam[0] + (dart_width / 2) * vx
        leg2_y = center_point_on_seam[1] + (dart_width / 2) * vy
        
        dart_leg1 = Line([(leg1_x, leg1_y), dart_tip])
        dart_leg2 = Line([(leg2_x, leg2_y), dart_tip])
        
        return [dart_leg1, dart_leg2]

    else:
        # Fallback for curved lines or more complex scenarios
        print("Warning: Dart creation on curved lines is not fully implemented.")
        return []
