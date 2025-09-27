import cv2 as cv
import numpy as np
from scipy.interpolate import make_interp_spline
from drafting_util import *

# v-necks are actually a slight curve, so this is a steep quadratic function
def draw_v_neckline(img, center_x, deepest_y, neckline_radius, shoulder_y, color, thickness):
  outer_x = center_x + neckline_radius

  a = (shoulder_y - deepest_y)/pow(outer_x - center_x, 2)
  fx = lambda x: a * pow(x - center_x, 2) + deepest_y

  x_smooth = np.linspace(center_x, outer_x, 10)
  y_smooth = fx(x_smooth)

  draw_curve(img, x_smooth, y_smooth, color, thickness)

def draw_square_neckline(img, center_x, neck_depth, shoulder_height, neck_radius, color, thickness):
  outer_x = center_x + neck_radius

  draw_vertical_line(img, outer_x, shoulder_height, shoulder_height + neck_depth, color, thickness)
  draw_horizantal_line(img, shoulder_height + neck_depth, center_x, outer_x, color, thickness)


def draw_scoop_neckline(img, center, outer_point, bottom_width, color, thickness):
  a = (outer_point[1] - center[1])/pow(outer_point[0] - center[0], 2)
  fx = lambda x: a * pow(x - center[0], 4) + center[1] 

  x_smooth = np.linspace(center[0], outer_point[0], 10)
  y_smooth = fx(x_smooth)

  print(x_smooth)
  print(y_smooth)

  draw_curve(img, x_smooth, y_smooth, color, thickness)