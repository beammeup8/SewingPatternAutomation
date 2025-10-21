import cv2 as cv
import numpy as np
import math
from scipy.interpolate import make_interp_spline

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

    return list(np.stack((fx(steps), fy(steps)), axis=-1))

def draw_line_at_angle(img, start_x, start_y, angle, end_x, color, thickness):
  angle = math.radians(angle)
  end_y = start_y + round(math.tan(angle) * (end_x - start_x))
  print(end_x, end_y)
  cv.line(img, (start_x, start_y), (end_x, end_y), color, thickness)

def draw_curve(img, x_points, y_points, color, thickness):
  points = np.stack((x_points, y_points), axis=-1).astype(np.int32)
  curve_points = points.reshape((-1, 1, 2))
  cv.polylines(img, [curve_points], color=color, isClosed=False, thickness=thickness)
  return curve_points

def create_horizontal_line(y, start_x, end_x):
  return [Line([(start_x, y), (end_x, y)])]

def create_vertical_line(x, start_y, end_y):
  return [Line([(x, start_y), (x, end_y)])]

def draw_lines(img, lines, color, thickness, offset=(0, 0)):
  for line in lines:
    # Get the final render points, which will be smoothed if the line is smooth.
    render_points = line.get_render_points()
    # Apply the offset to the final points before drawing.
    offset_points = [(p[0] + offset[0], p[1] + offset[1]) for p in render_points]
    
    points_array = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))
    cv.polylines(img, [points_array], isClosed=False, color=color, thickness=thickness)
