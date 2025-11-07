from util.line import Line
import math
class PatternPiece:
  """
  Represents a single piece of a sewing pattern, like a front, back, or sleeve.
  """
  def __init__(self, name, body_lines=None, drafting_lines=None, pattern_lines=None):
    """
    Initializes a PatternPiece.

    Args:
      name: The name of the pattern piece (e.g., "Front Bodice").
      body_lines: An optional list of body Line objects.
      drafting_lines: An optional list of drafting Line objects.
      pattern_lines: An optional list of pattern Line objects.
    """
    self.name = name
    self.body_lines = body_lines if body_lines is not None else []
    self.drafting_lines = drafting_lines if drafting_lines is not None else []
    self.pattern_lines = pattern_lines if pattern_lines is not None else []
    self.grainline = None # Will be a tuple of (list[Line], "text")

  def get_all_lines(self):
    """
    Returns a single list containing all lines from all types.
    """
    return self.body_lines + self.drafting_lines + self.pattern_lines

  def get_bounding_box(self):
    """
    Calculates the bounding box that encompasses all lines in this piece.
    Returns (min_x, min_y, max_x, max_y) in inches.
    """
    all_points = []
    for line in self.pattern_lines:
        # Use get_render_points to account for smoothed curves
        all_points.extend(line.get_render_points())
    
    if not all_points:
        return (0, 0, 0, 0)

    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    
    return (min_x, min_y, max_x, max_y)

  def add_grainline(self, length_in=5, angle=90, arrowhead_length=0.5, arrowhead_angle=25):
      """Adds a standard grainline arrow to the center of the piece."""
      min_x, min_y, max_x, max_y = self.get_bounding_box()
      center_x = (min_x + max_x) / 2
      center_y = (min_y + max_y) / 2

      half_len = length_in / 2
      line_angle_rad = math.radians(angle)

      sx = center_x - half_len * math.cos(line_angle_rad)
      sy = center_y - half_len * math.sin(line_angle_rad)
      ex = center_x + half_len * math.cos(line_angle_rad)
      ey = center_y + half_len * math.sin(line_angle_rad)
      start_point = (sx, sy)
      end_point = (ex, ey)

      # Create points for a single polyline representing the arrow
      arrow_points = [
          (ex - arrowhead_length * math.cos(line_angle_rad - math.radians(arrowhead_angle)), ey - arrowhead_length * math.sin(line_angle_rad - math.radians(arrowhead_angle))),
          end_point,
          (ex - arrowhead_length * math.cos(line_angle_rad + math.radians(arrowhead_angle)), ey - arrowhead_length * math.sin(line_angle_rad + math.radians(arrowhead_angle))),
          end_point,
          start_point,
          (sx + arrowhead_length * math.cos(line_angle_rad - math.radians(arrowhead_angle)), sy + arrowhead_length * math.sin(line_angle_rad - math.radians(arrowhead_angle))),
          start_point,
          (sx + arrowhead_length * math.cos(line_angle_rad + math.radians(arrowhead_angle)), sy + arrowhead_length * math.sin(line_angle_rad + math.radians(arrowhead_angle))),
      ]

      self.grainline = ([Line(arrow_points)], None)

  def add_fold_line(self, margin_in=1, x_coord=0):
      """Adds a 'Cut on Fold' indicator along the center front (x=0)."""
      # Find the min and max Y of the center front line from the pattern lines
      cf_points = [p for line in self.pattern_lines for p in line.get_render_points() if p[0] == x_coord]
      if not cf_points:
          print("Warning: Could not add fold line. No line found at x={x_coord}.")
          return

      min_y = min(p[1] for p in cf_points)
      max_y = max(p[1] for p in cf_points)

      line_x = margin_in
      shaft = Line([(line_x, min_y + margin_in), (line_x, max_y - margin_in)])
      top_y = min_y + margin_in
      bottom_y = max_y - margin_in
      top_t = Line([(line_x - margin_in, top_y), (line_x, top_y)])
      bottom_t = Line([(line_x - margin_in, bottom_y), (line_x, bottom_y)])

      self.grainline = ([shaft, top_t, bottom_t], "CUT ON FOLD")
