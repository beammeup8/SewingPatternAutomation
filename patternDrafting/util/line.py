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

    fx = make_interp_spline(t, points_arr[:, 0], k=k, bc_type='natural')
    fy = make_interp_spline(t, points_arr[:, 1], k=k, bc_type='natural')

    # Cache the render, so it will not be redone
    self.points = list(np.stack((fx(steps), fy(steps)), axis=-1))
    self.smooth = False 

    return self.points

  def __add__(self, other):
    """Combines two Line objects by concatenating their points."""
    if not isinstance(other, Line):
      return NotImplemented
    new_points = self.points + other.points
    return Line(new_points, smooth=self.smooth or other.smooth)

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
