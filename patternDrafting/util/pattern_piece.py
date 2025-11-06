class PatternPiece:
  """
  Represents a single piece of a sewing pattern, like a front, back, or sleeve.
  """
  def __init__(self, name, offset_in=(0, 0), body_lines=None, drafting_lines=None, pattern_lines=None):
    """
    Initializes a PatternPiece.

    Args:
      name: The name of the pattern piece (e.g., "Front Bodice").
      offset_in: A tuple (x, y) representing the layout offset in inches.
      body_lines: An optional list of body Line objects.
      drafting_lines: An optional list of drafting Line objects.
      pattern_lines: An optional list of pattern Line objects.
    """
    self.name = name
    self.offset_in = offset_in
    self.body_lines = body_lines if body_lines is not None else []
    self.drafting_lines = drafting_lines if drafting_lines is not None else []
    self.pattern_lines = pattern_lines if pattern_lines is not None else []

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
