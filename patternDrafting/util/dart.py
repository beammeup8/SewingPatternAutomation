from .line import Line
import math

class Dart:
    """Represents a dart in a sewing pattern."""

    def __init__(self, seam_line, center_point_on_seam, dart_width, dart_tip, name=None):
        """
        Initializes a Dart object.

        Args:
            seam_line (Line): The line (can be straight or curved) where the dart opens.
            center_point_on_seam (tuple): The (x, y) point on the seam line where the dart is centered.
            dart_width (float): The total width of the dart opening, measured along the seam.
            dart_tip (tuple): The (x, y) point of the dart's tip.
            name (str, optional): The name of the dart (e.g., "Bust Dart"). Defaults to None.
        """
        self.tip = dart_tip
        self.name = name
        self.seam_line = seam_line
        self.leg1 = None
        self.leg2 = None
        self.extended_legs = []

        # This is a simplified approach for straight lines. A curved line would
        # require walking along the curve's points to measure arc length.
        if len(seam_line.points) == 2:
            p1_x, p1_y = seam_line.points[0]
            p2_x, p2_y = seam_line.points[1]

            # Determine the direction vector of the seam line
            line_length = math.dist((p1_x, p1_y), (p2_x, p2_y))
            if line_length == 0: 
                return
            
            vx = (p2_x - p1_x) / line_length
            vy = (p2_y - p1_y) / line_length

            # Calculate the positions of the dart legs on the seam line
            leg1_x = center_point_on_seam[0] - (dart_width / 2) * vx
            leg1_y = center_point_on_seam[1] - (dart_width / 2) * vy
            leg2_x = center_point_on_seam[0] + (dart_width / 2) * vx
            leg2_y = center_point_on_seam[1] + (dart_width / 2) * vy
            
            self.leg1 = Line([(leg1_x, leg1_y), dart_tip])
            self.leg2 = Line([(leg2_x, leg2_y), dart_tip])

        else:
            # Fallback for curved lines or more complex scenarios
            print("Warning: Dart creation on curved lines is not fully implemented.")
    
    def get_lines(self):
        """
        Returns a list of all Line objects that constitute the dart.
        This includes the main legs and any extended lines for truing.
        """
        lines = []
        if self.leg1: lines.append(self.leg1)
        if self.leg2: lines.append(self.leg2)
        return lines

    def extend_legs_to_cut_line(self, cut_lines):
        """
        Extends the dart legs from the tip outwards to intersect with the cut line.
        The extended lines are stored in `self.extended_legs`.
        Extends the dart legs from the tip outwards to intersect with the cut line
        by appending the intersection point to the leg's points list.

        Args:
            cut_lines (list[Line]): The lines representing the seam allowance/cut lines.
        """
        if not self.leg1 or not self.leg2:
            return

        extended_legs = []
        if not cut_lines: return
        
        for leg in [self.leg1, self.leg2]:
            # The leg goes from the seam to the tip. We need to extend from the tip outwards.
            # For a straight dart, this is points[0] and points[1].
            # For a curved dart, we take the last two points to get the direction at the tip.
            p_tip = leg.points[-1]
            p_before_tip = leg.points[-2] if len(leg.points) > 1 else leg.points[0]

            # Calculate the direction vector from the tip outwards
            vx = p_tip[0] - p_before_tip[0]
            vy = p_tip[1] - p_before_tip[1]
            
            # Create a very long line segment starting from the tip and going outwards
            # A large multiplier ensures it will cross the cut line.
            p_far = (p_tip[0] + vx * 100, p_tip[1] + vy * 100)
            
            # Find intersection between the extended leg and all cut lines
            closest_intersection = None
            min_dist_sq = float('inf')
            
            for cut_line in cut_lines:
                intersection = cut_line.get_intersection(Line([p_tip, p_far]))
                if intersection:
                    dist_sq = math.dist(p_tip, intersection) ** 2
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        closest_intersection = intersection

            if closest_intersection:
                # Create a new line from the dart tip to the intersection point on the cut line
                extended_legs.append(Line([p_tip, closest_intersection]))
                # Add the new point to the existing dart leg line
                leg.points.append(closest_intersection)
            else:
                # This might happen if the dart is very unusual or the cut line is complex.
                # As a fallback, we can just use the original leg.
                print(f"Warning: Could not extend dart leg to cut line. Using original leg.")
                extended_legs.append(leg)

        self.extended_legs = extended_legs
