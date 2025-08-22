import cv2 as cv
import numpy as np
from scipy.interpolate import make_interp_spline

def draw_horizantal_line(img, y, start_x, end_x, color, thickness):
  cv.line(img, (start_x, y), (end_x, y), color, thickness)

def draw_vertical_line(img, x, start_y, end_y, color, thickness):
  cv.line(img, (x, start_y), (x, end_y), color, thickness)

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

