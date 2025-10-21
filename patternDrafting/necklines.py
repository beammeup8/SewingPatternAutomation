import cv2 as cv
import numpy as np
from scipy.interpolate import make_interp_spline
from drafting_util import *

# v-necks are actually a slight curve, so this is a steep quadratic function
def create_v_neckline(center_x, neckline_depth, neckline_radius, shoulder_y):
  outer_x = center_x + neckline_radius

  a = (shoulder_y - neckline_depth)/pow(outer_x - center_x, 2)
  fx = lambda x: a * pow(x - center_x, 2) + neckline_depth

  x_smooth = np.linspace(center_x, outer_x, 50)
  y_smooth = fx(x_smooth)

  points = list(np.stack((x_smooth, y_smooth), axis=-1))
  return [Line(points)]

def create_square_neckline(center_x, neck_depth, shoulder_height, neck_radius):
  outer_x = center_x + neck_radius
  deepest_y = shoulder_height + neck_depth

  side_line = create_vertical_line(outer_x, shoulder_height, deepest_y)
  bottom_line = create_horizontal_line(deepest_y, center_x, outer_x)
  return side_line + bottom_line

def create_scoop_neckline(center_x, neckline_depth, neckline_radius, shoulder_y):
  outer_x = center_x + neckline_radius
  a = (shoulder_y - neckline_depth)/pow(neckline_radius, 6)
  fx = lambda x: a * pow(x - center_x, 6) + neckline_depth
  x_smooth = np.linspace(center_x, outer_x, 50)
  y_smooth = fx(x_smooth)
  points = list(np.stack((x_smooth, y_smooth), axis=-1))
  return [Line(points)]