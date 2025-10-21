import cv2 as cv
import numpy as np
from scipy.interpolate import make_interp_spline
from drafting_util import *

# v-necks are actually a slight curve, so this is a steep quadratic function
def create_v_neckline(center_x, shoulder_height, neckline_depth, neckline_radius):
  outer_x = center_x + neckline_radius
  bottom_y = shoulder_height + neckline_depth

  a = -(neckline_depth)/pow(outer_x - center_x, 2)
  fx = lambda x: a * pow(x - center_x, 2) + bottom_y

  x_smooth = np.linspace(center_x, outer_x, 50)
  y_smooth = fx(x_smooth)

  points = list(np.stack((x_smooth, y_smooth), axis=-1))
  return [Line(points, smooth=True)]

def create_square_neckline(center_x, shoulder_height, neckline_depth, neck_radius):
  outer_x = center_x + neck_radius
  bottom_y = shoulder_height + neckline_depth

  side_line = create_vertical_line(outer_x, shoulder_height, bottom_y)
  bottom_line = create_horizontal_line(bottom_y, center_x, outer_x)
  return side_line + bottom_line

def create_scoop_neckline(center_x, shoulder_height, neckline_depth, neckline_radius):
  outer_x = center_x + neckline_radius
  bottom_y = shoulder_height + neckline_depth

  a = -(neckline_depth)/pow(neckline_radius, 4)
  fx = lambda x: a * pow(x - center_x, 4) + bottom_y
  x_smooth = np.linspace(center_x, outer_x, 50)
  y_smooth = fx(x_smooth)
  points = list(np.stack((x_smooth, y_smooth), axis=-1))
  return [Line(points, smooth=True)]