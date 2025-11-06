import cv2 as cv
import numpy as np

# Define colors associated with line types
LINE_COLOR = (255, 255, 255)
BODY_COLOR = (255, 0, 0)
DRAFTING_COLOR = (0, 255, 0)

BACKGROUND_COLOR = (0, 0, 0)
THICKNESS = 10

def draw_pattern(canvas_size_in, scale, pattern_pieces, output_filepath, output=True):
  """
  Creates an image and draws all specified line groups onto it.

  Args:
    canvas_size_in: A tuple (width, height) for the image in inches.
    scale: The scale factor (pixels per inch).
    background_color: The background color of the image.
    pattern_pieces: A list of PatternPiece objects to draw.
    output_filepath: The path to save the final image file.
  """
  total_x_in, total_y_in = canvas_size_in

  # Image dimensions in pixels
  img_width_px = round(total_x_in * scale)
  img_height_px = round(total_y_in * scale)
  img = np.full((img_height_px, img_width_px, 3), BACKGROUND_COLOR, dtype=np.uint8)

  for piece in pattern_pieces:
    draw_lines(img, piece.body_lines, BODY_COLOR, scale=scale, offset=piece.offset_in)
    draw_lines(img, piece.drafting_lines, DRAFTING_COLOR, scale=scale, offset=piece.offset_in)
    draw_lines(img, piece.pattern_lines, LINE_COLOR, scale=scale, offset=piece.offset_in)
  
  if output:
    cv.imwrite(output_filepath, img)
  return img

def draw_lines(img, lines, color, scale=1, offset=(0, 0)):
  for line in lines:
    # Get the final render points, which will be smoothed if the line is smooth.
    render_points = line.get_render_points()
    # Apply offset (in inches), scale, and round to integer pixel coordinates
    offset_points = [(round((p[0] + offset[0]) * scale), round((p[1] + offset[1]) * scale)) for p in render_points]
    
    points_array = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))
    cv.polylines(img, [points_array], isClosed=False, color=color, thickness=THICKNESS)
