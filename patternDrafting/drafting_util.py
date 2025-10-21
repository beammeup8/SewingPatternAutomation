import cv2 as cv
import numpy as np
import math
from scipy.interpolate import make_interp_spline

class Line:
  def __init__(self, points, smooth=False):
    self.points = points
    self.smooth = smooth

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

def draw__smooth_curve(img, points, color, thickness):
  if len(points) <= 2:
    # This should be a line or a point
    return 

  # Choose spline degree based on number of points
  k = len(points) - 1
  
  points = np.array(points)
  t = np.arange(len(points))

  steps = np.linspace(t.min(), t.max(), 500)
  fx = make_interp_spline(t, points[:, 0], k=k)
  fy = make_interp_spline(t, points[:, 1], k=k)

  return draw_curve(img, fx(steps), fy(steps), color, thickness)

def create_horizontal_line(y, start_x, end_x):
  return [Line([(start_x, y), (end_x, y)])]

def create_vertical_line(x, start_y, end_y):
  return [Line([(x, start_y), (x, end_y)])]

def draw_lines(img, lines, color, thickness):
  for line in lines:
    x_points, y_points = zip(*(line.points))
    points = np.stack((x_points, y_points), axis=-1).astype(np.int32)
    curve_points = points.reshape((-1, 1, 2))
    cv.polylines(img, [curve_points], color=color, isClosed=False, thickness=thickness)

