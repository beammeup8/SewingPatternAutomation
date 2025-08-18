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

  draw_curve(img, fx(steps), fy(steps), color, thickness)


# v-necks are actually a slight curve, so this is a steep quadratic function
def draw_v_neckline(img, center, outer_point, color, thickness):
  a = (outer_point[1] - center[1])/pow(outer_point[0] - center[0], 2)
  fx = lambda x: a * pow(x - center[0], 2) + center[1] 

  x_smooth = np.linspace(center[0], outer_point[0], 10)
  y_smooth = fx(x_smooth)

  draw_curve(img, x_smooth, y_smooth, color, thickness)

def draw_square_neckline(img, center_x, neck_depth, shoulder_height, neck_radius, color, thickness):
  outer_x = center_x + neck_radius

  draw_vertical_line(img, outer_x, shoulder_height, shoulder_height + neck_depth, color, thickness)
  draw_horizantal_line(img, shoulder_height +neck_depth, center_x, outer_x, color, thickness)


def draw_scoop_neckline(img, center, outer_point, bottom_width, color, thickness):
  a = (outer_point[1] - center[1])/pow(outer_point[0] - center[0], 2)
  fx = lambda x: a * pow(x - center[0], 4) + center[1] 

  x_smooth = np.linspace(center[0], outer_point[0], 10)
  y_smooth = fx(x_smooth)

  print(x_smooth)
  print(y_smooth)

  draw_curve(img, x_smooth, y_smooth, color, thickness)

