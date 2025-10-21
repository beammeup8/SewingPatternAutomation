import cv2 as cv
import numpy as np
from scipy.interpolate import make_interp_spline
from util.line import Line

# v-necks are actually a slight curve, so this is a steep quadratic function
def create_v_neckline(shoulder_height, neckline_depth, neckline_radius):
  a = (shoulder_height - neckline_depth)/pow(neckline_radius, 2)
  fx = lambda x: a * pow(x, 2) + neckline_depth

  x_smooth = np.linspace(0,neckline_radius, 50)
  y_smooth = fx(x_smooth)

  points = list(np.stack((x_smooth, y_smooth), axis=-1))
  return Line(points, smooth=True)

def create_square_neckline(shoulder_height, neckline_depth, neckline_radius):
  side_line = Line.vertical(neckline_radius, shoulder_height, neckline_depth)
  bottom_line = Line.horizontal(neckline_depth, 0, neckline_radius)
  return side_line + bottom_line

def create_scoop_neckline(shoulder_height, neckline_depth, neckline_radius):
  a = (shoulder_height - neckline_depth)/pow(neckline_radius, 6)
  fx = lambda x: a * pow(x, 6) + neckline_depth

  x_smooth = np.linspace(0, neckline_radius, 50)
  y_smooth = fx(x_smooth)
  
  points = list(np.stack((x_smooth, y_smooth), axis=-1))
  return Line(points, smooth=True)