import cv2 as cv
import numpy as np
from datetime import date

# Define colors associated with line types
LINE_COLOR = (255, 255, 255)
BODY_COLOR = (255, 0, 0)
DRAFTING_COLOR = (0, 255, 0)

BACKGROUND_COLOR = (0, 0, 0)
THICKNESS = 10

def draw_pattern(canvas_size_in, scale, pattern_pieces, output_filepath, pattern_name, output=True):
  """
  Creates an image and draws all specified line groups onto it.

  Args:
    canvas_size_in: A tuple (width, height) for the image in inches.
    scale: The scale factor (pixels per inch).
    pattern_pieces: A list of PatternPiece objects to draw. 
    output_filepath: The path to save the final image file.
    pattern_name: The name of the overall pattern.
    output: A boolean to control if the image is saved to a file.
  """
  total_x_in, total_y_in = canvas_size_in

  # Image dimensions in pixels
  img_width_px = round(total_x_in * scale)
  img_height_px = round(total_y_in * scale)
  img = np.full((img_height_px, img_width_px, 3), BACKGROUND_COLOR, dtype=np.uint8)

  for piece in pattern_pieces:
    draw_lines(img, piece.body_lines, BODY_COLOR, THICKNESS, scale=scale, offset=piece.offset_in)
    draw_lines(img, piece.drafting_lines, DRAFTING_COLOR, THICKNESS, scale=scale, offset=piece.offset_in)
    draw_lines(img, piece.pattern_lines, LINE_COLOR, THICKNESS, scale=scale, offset=piece.offset_in)

    _draw_label(img, piece, pattern_name, scale)
  
  cv.imwrite(output_filepath, img)

def _draw_label(img, piece, pattern_name, scale):
    """Draws the name, pattern name, and date on a pattern piece."""
    # Create a mask of the pattern piece to find a safe label area
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    # Combine all pattern line points into a single contour
    all_points = []
    for line in piece.pattern_lines:
        all_points.extend(line.get_render_points())

    if not all_points:
        print(f"Warning: Cannot draw label for piece '{piece.name}'. Not enough space.")
        return

    # Scale and offset points for drawing on the mask
    contour_px = np.array([
        (round((p[0] + piece.offset_in[0]) * scale), round((p[1] + piece.offset_in[1]) * scale))
        for p in all_points
    ], dtype=np.int32)

    cv.fillPoly(mask, [contour_px], 255)

    # Erode the mask to find a safe inner area
    inset_px = int(min(img.shape[:2]) * 0.08) # 8% of smallest image dimension
    kernel = np.ones((inset_px, inset_px), np.uint8)
    eroded_mask = cv.erode(mask, kernel, iterations=1)

    # Find the bounding box of the safe area
    contours, _ = cv.findContours(eroded_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"Warning: Cannot draw label for piece '{piece.name}'. No safe area found after erosion.")
        return

    x, y, w, h = cv.boundingRect(max(contours, key=cv.contourArea))

    today_str = date.today().strftime("%Y-%m-%d")
    labels = [piece.name, pattern_name, today_str]
    font = cv.FONT_HERSHEY_SIMPLEX

    # Dynamically determine font scale
    font_scale = 1
    while True:
        text_size = cv.getTextSize(max(labels, key=len), font, font_scale, THICKNESS)[0]
        if text_size[0] > w or text_size[1] * len(labels) > h:
            font_scale *= 0.9
            break
        font_scale *= 1.1

    line_height = cv.getTextSize(labels[0], font, font_scale, THICKNESS)[0][1] * 1.5
    total_text_height = line_height * (len(labels) - 1)
    start_y_px = y + (h / 2) - (total_text_height / 2)

    for i, text in enumerate(labels):
        cv.putText(img, text, (x, int(start_y_px + i * line_height)), font, font_scale, LINE_COLOR, THICKNESS)

def draw_lines(img, lines, color, thickness, scale=1, offset=(0, 0)):
  for line in lines:
    # Get the final render points, which will be smoothed if the line is smooth.
    render_points = line.get_render_points()
    # Apply offset (in inches), scale, and round to integer pixel coordinates
    offset_points = [(round((p[0] + offset[0]) * scale), round((p[1] + offset[1]) * scale)) for p in render_points]
    
    points_array = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))
    cv.polylines(img, [points_array], isClosed=False, color=color, thickness=thickness)
