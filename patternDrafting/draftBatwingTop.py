# Drafting loosely following this tutorial

import cv2 as cv
import numpy as np

COLOR = (255, 255, 255)
BODY_COLOR = (255, 0, 0)
DRAFTING_COLOR = (0, 255, 0)
THICKNESS = 10
SCALE = 100
BOARDER = 2

def scale(inches):
  return round(SCALE * inches)


def draft(measurements, garment_specs):
  total_x = 10000
  total_y = 10000

  img = np.zeros((total_x, total_y, 3), dtype=np.uint8)

  spacing = scale(BOARDER)
  # Draw drafting lines
  center_x = spacing
  front_top_y = spacing

  garm_length = measurements['shoulder to waist'] + measurements['waist to hip'] - garment_specs['height above hip']
  front_hem_point = front_top_y + scale(garm_length)
  cv.line(img, (center_x, front_top_y), (center_x, front_hem_point), COLOR, THICKNESS)
  
  back_top_y = spacing + front_hem_point
  back_hem_point = back_top_y + scale(garm_length)
  cv.line(img, (center_x, back_top_y), (center_x, back_hem_point), COLOR, THICKNESS)
  
  # shoulder line
  shoulder_x = center_x + scale(measurements['shoulders']/2)
  cv.line(img, (center_x, front_top_y), (shoulder_x, front_top_y), BODY_COLOR, THICKNESS)

  # bust line
  bust_x = center_x + scale(measurements['bust']/4)
  bust_y = front_top_y + scale(measurements['shoulder to bust'])
  cv.line(img, (center_x, bust_y), (bust_x, bust_y), BODY_COLOR, THICKNESS)

  # waist line
  waist_x = center_x + scale(measurements['waist']/4)
  waist_y = front_top_y + scale(measurements['shoulder to waist'])
  cv.line(img, (center_x, waist_y), (waist_x, waist_y), BODY_COLOR, THICKNESS)

  # hip line
  hip_x = center_x + scale(measurements['hip']/4)
  hip_y = front_top_y + scale(measurements['shoulder to waist'] + measurements['waist to hip'])
  cv.line(img, (center_x, hip_y), (hip_x, hip_y), BODY_COLOR, THICKNESS)

  # Sleeve Line
  sleeve_edge_x = center_x + scale(garment_specs['sleeve length'] + measurements['shoulders']/2)
  sleeve_edge_y = round((front_top_y + scale(measurements['shoulder to bust']))/2)
  cv.line(img, (center_x, sleeve_edge_y), (sleeve_edge_x, sleeve_edge_y), DRAFTING_COLOR, THICKNESS)

  return img, (total_x/ SCALE, total_y/ SCALE)



if __name__ == "__main__":
  measurements = {}
  measurements['bust'] = 56
  measurements['waist'] = 45
  measurements['hip'] = 56
  measurements['shoulders'] = 19
  measurements['shoulder to bust'] = 12
  measurements['shoulder to waist'] = 18
  measurements['waist to hip'] = 10
  measurements['above elbow circumference'] = 16

  garment_specs = {}
  garment_specs['sleeve length'] = 8
  garment_specs['height above hip'] = 1
  garment_specs['front neckline depth'] = 4.5
  garment_specs['back neckline depth'] = 2
  garment_specs['neckline radius'] = 7
  garment_specs['waist ease'] = 1
  garment_specs['hip ease'] = 1.5


  img,size = draft(measurements, garment_specs)
  cv.imwrite("testFiles/batwingDraft.png", img)


