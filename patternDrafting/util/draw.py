import cv2 as cv
import numpy as np

def draw_lines(img, lines, color, thickness, offset=(0, 0)):
  for line in lines:
    # Get the final render points, which will be smoothed if the line is smooth.
    render_points = line.get_render_points()
    # Apply the offset to the final points before drawing.
    offset_points = [(p[0] + offset[0], p[1] + offset[1]) for p in render_points]
    
    points_array = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))
    cv.polylines(img, [points_array], isClosed=False, color=color, thickness=thickness)
