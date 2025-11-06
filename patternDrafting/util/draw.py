import cv2 as cv
import numpy as np

def draw_lines(img, lines, color, thickness, scale=100, offset=(0, 0)):
  for line in lines:
    # Get the final render points, which will be smoothed if the line is smooth.
    render_points = line.get_render_points()
    # Apply offset (in inches), scale, and round to integer pixel coordinates
    offset_points = [(round((p[0] + offset[0]) * scale), round((p[1] + offset[1]) * scale)) for p in render_points]
    
    points_array = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))
    cv.polylines(img, [points_array], isClosed=False, color=color, thickness=thickness)
