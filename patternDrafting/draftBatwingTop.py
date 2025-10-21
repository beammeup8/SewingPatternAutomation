# Drafting loosely following this tutorial

import cv2 as cv
import numpy as np

from necklines import *
from util.line import Line
from util.draw import draw_lines


BACKGROUND_COLOR = (0, 0, 0)
LINE_COLOR = (255, 255, 255)
BODY_COLOR = (255, 0, 0)
DRAFTING_COLOR = (0, 255, 0)
THICKNESS = 10
SCALE = 100
BOARDER = 2

def scale(inches):
  return round(SCALE * inches)

def draft(measurements, garment_specs):
  total_x = 5000
  total_y = 10000

  img = np.full((total_y, total_x, 3), BACKGROUND_COLOR, dtype=np.uint8)

  body_lines = []
  drafting_lines = []
  pattern_lines = []

  spacing = scale(BOARDER)

  # Draw drafting lines
  center_x = 0
  front_top_y = 0

  garm_length = measurements['shoulder to waist'] + measurements['waist to hip'] - garment_specs['height above hip']
  front_hem_point = front_top_y + scale(garm_length)
  front_neckline_depth = scale(garment_specs['front neckline depth'])
  front_neck_point = front_top_y + front_neckline_depth
  # Center front line (body)
  body_lines.append(Line.vertical(center_x, front_top_y, front_hem_point))
  # Center front line (pattern)
  pattern_lines.append(Line.vertical(center_x, front_neck_point, front_hem_point))

  # shoulder line
  shoulder_x = center_x + scale(measurements['shoulders']/2)
  body_lines.append(Line.horizontal(front_top_y, center_x, shoulder_x))

  # neckline
  neckline_radius_scaled = scale(garment_specs['neckline radius'])
  outer_x = center_x + neckline_radius_scaled
  
  # This is currently drawing all three neckline options on top of each other.
  # You can comment out the ones you don't want to see.
  
  # Square neckline 
  pattern_lines.append(create_square_neckline(front_top_y, front_neck_point, neckline_radius_scaled))
  # V-neckline 
  pattern_lines.append(create_v_neckline(front_top_y, front_neck_point, neckline_radius_scaled))
  # Scoop neckline 
  pattern_lines.append(create_scoop_neckline(front_top_y, front_neck_point, neckline_radius_scaled))

  # upper bust line
  upper_bust_x = center_x + scale(measurements['upper bust']/4)
  upper_bust_y = front_top_y + scale(measurements['shoulder to armpit'])
  body_lines.append(Line.horizontal(upper_bust_y, center_x, upper_bust_x))
  
  # bust line
  bust_x = center_x + scale(measurements['bust']/4)
  bust_y = front_top_y + scale(measurements['shoulder to bust'])
  body_lines.append(Line.horizontal(bust_y, center_x, bust_x))

  # waist line
  waist_x = center_x + scale(measurements['waist']/4)
  waist_y = front_top_y + scale(measurements['shoulder to waist'])
  body_lines.append(Line.horizontal(waist_y, center_x, waist_x))

  # high hip line
  high_hip_x = center_x + scale(measurements['high hip']/4)
  high_hip_y = front_top_y + scale(measurements['shoulder to waist'] + measurements['waist to high hip'])
  body_lines.append(Line.horizontal(high_hip_y, center_x, high_hip_x))

  # hip line
  hip_x = center_x + scale(measurements['hip']/4)
  hip_y = front_top_y + scale(measurements['shoulder to waist'] + measurements['waist to hip'])
  body_lines.append(Line.horizontal(hip_y, center_x, hip_x))

  # Sleeve Lines
  sleeve_edge_x = center_x + scale(garment_specs['sleeve length'] + measurements['shoulders']/2)
  armpit_depth = scale(measurements['shoulder to bust'])
  sleeve_edge_y = round((front_top_y + armpit_depth)/2)
  drafting_lines.append(Line.horizontal(sleeve_edge_y, center_x, sleeve_edge_x))

  neckline_outside_x = center_x + neckline_radius_scaled
  pattern_lines.append(Line.horizontal(front_top_y, neckline_outside_x, shoulder_x))

  sleeve_width = scale(garment_specs['cuff ease']) + scale(measurements['above elbow circumference'])
  cuff_top_y = sleeve_edge_y - round(sleeve_width/4)
  cuff_bottom_y = sleeve_edge_y + round(sleeve_width/4)
  pattern_lines.append(Line.vertical(sleeve_edge_x, cuff_top_y, cuff_bottom_y))

  pattern_lines.append(Line([(shoulder_x, front_top_y), (sleeve_edge_x, cuff_top_y)]))

  # Body Curve
  body_lines.append(Line([(upper_bust_x, upper_bust_y), (bust_x, bust_y), (waist_x, waist_y), (high_hip_x, high_hip_y), (hip_x, hip_y)], smooth=True))

  bust_ease = round(scale(garment_specs['bust ease'])/4)
  waist_ease = round(scale(garment_specs['waist ease'])/4)
  hip_ease = round(scale(garment_specs['hip ease'])/4)

  side_seam_line = Line([(sleeve_edge_x, cuff_bottom_y), (bust_x + bust_ease, bust_y), (waist_x + waist_ease, waist_y), (high_hip_x + hip_ease, high_hip_y), (hip_x + hip_ease, hip_y)], smooth=True)
  hem_line = Line([(center_x, front_hem_point), (hip_x + hip_ease, front_hem_point)])
  
  # The intersection logic has been removed. Adding the full lines for now.
  pattern_lines.append(side_seam_line)
  pattern_lines.append(hem_line)

  # Define layout offsets
  front_offset = (spacing, spacing)
  back_offset = (spacing, front_offset[1] + front_hem_point + spacing)

  draw_lines(img, body_lines, BODY_COLOR, THICKNESS, offset=front_offset)
  draw_lines(img, drafting_lines, DRAFTING_COLOR, THICKNESS, offset=front_offset)
  draw_lines(img, pattern_lines, LINE_COLOR, THICKNESS, offset=front_offset)

  return img, (total_x/ SCALE, total_y/ SCALE)



if __name__ == "__main__":
  measurements = {}
  measurements['upper bust'] = 49
  measurements['bust'] = 56
  measurements['waist'] = 45
  measurements['high hip'] = 54
  measurements['hip'] = 56
  measurements['shoulders'] = 19
  measurements['shoulder to armpit'] = 10
  measurements['shoulder to bust'] = 12
  measurements['shoulder to waist'] = 18
  measurements['waist to high hip'] = 6
  measurements['waist to hip'] = 10
  measurements['above elbow circumference'] = 16

  garment_specs = {}
  garment_specs['sleeve length'] = 8
  garment_specs['cuff ease'] = 1
  garment_specs['height above hip'] = 1
  garment_specs['front neckline depth'] = 7
  garment_specs['back neckline depth'] = 2
  garment_specs['neckline radius'] = 7
  garment_specs['bust ease'] = 0.5
  garment_specs['waist ease'] = 1
  garment_specs['hip ease'] = 1.5


  img,size = draft(measurements, garment_specs)
  print(size)
  cv.imwrite("testFiles/batwingDraft.png", img)
