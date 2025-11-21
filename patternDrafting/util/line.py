from scipy.interpolate import make_interp_spline
import numpy as np
import math
import enum

class Line:
  def __init__(self, points, smooth=False):
    self.points = points
    self.smooth = smooth

  def get_render_points(self):
    """
    Returns the list of points that make up the line, generating points for a
    smooth curve if necessary.
    """
    if not self.smooth or len(self.points) <= 2:
      return self.points

    k = min(len(self.points) - 1, 3)
    points_arr = np.array(self.points)
    t = np.arange(len(self.points))
    steps = np.linspace(t.min(), t.max(), 500)

    # Use 'natural' boundary conditions only when appropriate (cubic splines)
    bc_type = 'natural' if k == 3 else None

    fx = make_interp_spline(t, points_arr[:, 0], k=k, bc_type=bc_type)
    fy = make_interp_spline(t, points_arr[:, 1], k=k, bc_type=bc_type)

    return list(np.stack((fx(steps), fy(steps)), axis=-1))

  def __add__(self, other):
    """Combines two Line objects by concatenating their points."""
    if not isinstance(other, Line):
      return NotImplemented
    new_points = self.points + other.points
    return Line(new_points, smooth=self.smooth or other.smooth)

  def get_midpoint(self):
      """Calculates the midpoint of a straight line."""
      if len(self.points) != 2:
          # For polylines, this would be more complex (finding the center of the arc length)
          return self.points[len(self.points) // 2]
      p1, p2 = self.points
      return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

  def get_perpendicular_point(self, from_point, distance):
      """Calculates a point at a given distance perpendicular to the line from a specific point."""
      if len(self.points) != 2:
          return None # Not implemented for curves
      p1, p2 = self.points
      angle_rad = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
      perp_angle_rad = angle_rad + math.pi / 2
      
      new_x = from_point[0] + distance * math.cos(perp_angle_rad)
      new_y = from_point[1] + distance * math.sin(perp_angle_rad)
      return (new_x, new_y)

  def get_x_for_y(self, y):
      """Calculates the x-coordinate on a straight line for a given y-coordinate."""
      # Get the final rendered points, which may be smoothed.
      points = self.get_render_points()
      
      # Iterate through the line segments to find the intersection.
      for i in range(len(points) - 1):
          p1, p2 = points[i], points[i+1]
          y1, y2 = p1[1], p2[1]
          # Check if the target y is between the y-coordinates of the segment's points.
          if (y1 <= y <= y2) or (y2 <= y <= y1):
              if y2 - y1 != 0: # Avoid division by zero for horizontal segments.
                  return p1[0] + (y - y1) * (p2[0] - p1[0]) / (y2 - y1)
      return None # Return None if no intersection is found.

  @classmethod
  def horizontal(cls, y, start_x, end_x):
    """Creates a horizontal Line object."""
    return cls([(start_x, y), (end_x, y)])

  @classmethod
  def vertical(cls, x, start_y, end_y):
    """Creates a vertical Line object."""
    return cls([(x, start_y), (x, end_y)])

  @classmethod
  def from_angle(cls, start_x, start_y, angle, end_x):
    """Creates a Line object at a set angle."""
    rad_angle = math.radians(angle)
    end_y = start_y + (math.tan(rad_angle) * (end_x - start_x))
    return cls([(start_x, start_y), (end_x, end_y)])

  def _clip_line(self, bound, is_in_lambda, intersection_lambda):
      """Helper method to perform clipping against a single boundary."""
      if bound is None:
          return self.points

      input_points = self.get_render_points()
      clipped_points = []
      if not input_points:
          return []

      for i in range(len(input_points)):
          p1 = input_points[i-1] if i > 0 else input_points[i]
          p2 = input_points[i]
          p1_in = is_in_lambda(p1)
          p2_in = is_in_lambda(p2)

          if p2_in:
              if not p1_in:
                  # p1 is out, p2 is in: add intersection and p2
                  intersection_point = intersection_lambda(p1, p2)
                  if intersection_point: clipped_points.append(intersection_point)
              clipped_points.append(p2)
          elif p1_in:
              # p1 is in, p2 is out: add intersection
              intersection_point = intersection_lambda(p1, p2)
              if intersection_point: clipped_points.append(intersection_point)
      return clipped_points

  def truncate_horizontal(self, min_x=None, max_x=None):
    """
    Truncates the line in place to fit within horizontal bounds (min_x, max_x).
    """
    get_y_intersect = lambda b: (lambda p1, p2: (b, p1[1] + (p2[1] - p1[1]) * (b - p1[0]) / (p2[0] - p1[0])) if p2[0] - p1[0] != 0 else None)
    self.points = self._clip_line(min_x, lambda p: p[0] >= min_x, get_y_intersect(min_x))
    self.points = self._clip_line(max_x, lambda p: p[0] <= max_x, get_y_intersect(max_x))
    return self

  def truncate_vertical(self, min_y=None, max_y=None):
    """
    Truncates the line in place to fit within vertical bounds (min_y, max_y).
    """
    get_x_intersect = lambda b: (lambda p1, p2: (p1[0] + (p2[0] - p1[0]) * (b - p1[1]) / (p2[1] - p1[1]), b) if p2[1] - p1[1] != 0 else None)
    self.points = self._clip_line(min_y, lambda p: p[1] >= min_y, get_x_intersect(min_y))
    self.points = self._clip_line(max_y, lambda p: p[1] <= max_y, get_x_intersect(max_y))
    return self

  def get_intersection(self, other_line):
      """
      Finds the intersection point between this line and another line.
      This handles intersections between two straight lines or a straight line and a polyline.

      Args:
          other_line (Line): The line to check for intersection with.

      Returns:
          tuple: The (x, y) coordinates of the intersection, or None if no intersection exists.
      """
      # This implementation assumes `other_line` is a straight line segment.
      # It checks for intersection against all segments of `self`.
      if len(other_line.points) != 2:
          return None # Can only find intersection with a straight line.

      p1, p2 = other_line.points[0], other_line.points[1]
      x1, y1 = p1
      x2, y2 = p2

      line_segments = self.get_render_points()
      for i in range(len(line_segments) - 1):
          p3, p4 = line_segments[i], line_segments[i+1]
          x3, y3 = p3
          x4, y4 = p4

          denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
          if denominator == 0:
              continue # Lines are parallel

          t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
          u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

          if 0 <= t <= 1 and 0 <= u <= 1:
              # Intersection point
              return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
      return None
