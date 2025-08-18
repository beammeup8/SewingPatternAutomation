import cv2 as cv
import numpy as np
from scipy.interpolate import make_interp_spline

def draw_horizantal_line(img, y, start_x, end_x, color, thickness):
  cv.line(img, (start_x, y), (end_x, y), color, thickness)

def draw_vertical_line(img, x, start_y, end_y, color, thickness):
  cv.line(img, (x, start_y), (x, end_y), color, thickness)

def draw__smooth_curve(img, points, color, thickness):
  if len(points) <= 2:
    return  # Not enough points to draw a curve

  # Choose spline degree based on number of points
  k = min(3, len(points) - 1)
  
  points = np.array(points)
  t = np.arange(len(points))  # parameter: just the index

  # Parametric splines for x(t) and y(t)

  t_smooth = np.linspace(t.min(), t.max(), 500)
  x_spline = make_interp_spline(t, points[:, 0], k=k)
  y_spline = make_interp_spline(t, points[:, 1], k=k)

  x_smooth = x_spline(t_smooth)
  y_smooth = y_spline(t_smooth)

  curve_points = np.stack((x_smooth, y_smooth), axis=-1).astype(np.int32)
  curve_points = curve_points.reshape((-1, 1, 2))

  cv.polylines(img, [curve_points], color=color, isClosed=False, thickness=thickness)

