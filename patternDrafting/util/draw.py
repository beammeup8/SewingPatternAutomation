import cv2 as cv
import numpy as np
from datetime import date
import math
from .constants import *
from .line import Line


def draw_pattern(
    scale, pattern_pieces, seam_allowance, output_filepath, pattern_name, output=True
):
    """
    Calculates layout, creates an image, and draws all pattern pieces onto it.

    Args:
      scale: The scale factor (pixels per inch).
      pattern_pieces: A list of PatternPiece objects to draw.
      seam_allowance: The seam allowance in inches.
      output_filepath: The path to save the final image file.
      pattern_name: The name of the overall pattern.
      output: A boolean to control if the image is saved to a file.
    """
    # --- 1. Calculate Layout ---
    # Simple horizontal side-by-side layout
    layouts = []
    buffer_in = max(SPACING, seam_allowance * 1.5)
    total_height_in = 0
    current_x_in = buffer_in
    for piece in pattern_pieces:
        min_x, min_y, max_x, max_y = piece.get_bounding_box()
        piece_width = max_x - min_x
        piece_height = max_y - min_y
        
        # The offset positions the top-left of the piece's bounding box
        offset_x = current_x_in - min_x
        offset_y = buffer_in - min_y
        layouts.append({'offset': (offset_x, offset_y), 'piece': piece})
        
        current_x_in += piece_width + buffer_in
        total_height_in = max(total_height_in, piece_height)

    canvas_width_in = current_x_in
    canvas_height_in = total_height_in + 2 * buffer_in

    # Image dimensions in pixels
    img_width_px = round(canvas_width_in * scale)
    img_height_px = round(canvas_height_in * scale)
    img = np.full((img_height_px, img_width_px, 3), BACKGROUND_COLOR, dtype=np.uint8)

    # --- Draw Optional Grid ---
    if DRAW_GRID:
        # Draw vertical grid lines every inch
        for i in range(1, int(canvas_width_in)):
            x_pos = round(i * scale)
            cv.line(img, (x_pos, 0), (x_pos, img_height_px), GRID_COLOR, 1)
        # Draw horizontal grid lines every inch
        for i in range(1, int(canvas_height_in)):
            y_pos = round(i * scale)
            cv.line(img, (0, y_pos), (img_width_px, y_pos), GRID_COLOR, 1)

    # --- 2. Draw Pieces ---
    for layout in layouts:
        piece = layout['piece']
        offset = layout['offset']
        if DRAFTING_LINES:
            draw_lines(img, piece.body_lines, BODY_COLOR, scale=scale, offset=offset)
            draw_lines(img, piece.drafting_lines, DRAFTING_COLOR, scale=scale, offset=offset)
        # Draw internal marking lines (like darts) with the main pattern line style
        draw_lines(
            img,
            piece.marking_lines,
            LINE_COLOR,
            scale=scale,
            offset=offset,
        )
        # Draw the cut line (solid)
        draw_lines(
            img,
            piece.cut_lines,
            LINE_COLOR,
            scale=scale,
            offset=offset,
        )
        draw_lines(
            img,
            piece.pattern_lines,
            LINE_COLOR,
            scale=scale,
            offset=offset,
            is_dashed=True,
        )

        if piece.grainline:
            lines, text = piece.grainline
            draw_lines(img, lines, LINE_COLOR, scale=scale, offset=offset, thickness=TEXT_THICKNESS)

            label_font_size = _draw_label(img, piece, pattern_name, scale, offset)
            # Draw the "CUT ON FOLD" text if it exists
            if text:
                # Assume the first line in the list is the main shaft
                _draw_text_along_line(
                    img,
                    text,
                    lines[0],
                    offset,
                    scale,
                    LINE_COLOR,
                    label_font_size,
                )

    cv.imwrite(output_filepath, img)


def _draw_label(img, piece, pattern_name, scale, offset):
    """Draws the name, pattern name, and date on a pattern piece."""
    # Create a mask of the pattern piece to find a safe label area
    piece_contour = piece.get_outline_contour(scale=scale)
    if piece_contour is None:
        print(f"Warning: Could not create a contour for piece '{piece.name}'.")
        return

    # Get the piece's bounding box to correctly position the contour on the canvas
    min_x, min_y, _, _ = piece.get_bounding_box()
    contour_offset = (round((offset[0] + min_x - 1) * scale), round((offset[1] + min_y - 1) * scale))

    if DEBUG:
        # Draw the main outline contour for debugging purposes
        cv.drawContours(img, [piece_contour], -1, (0, 165, 255), 2, offset=contour_offset) # Orange

    # Create a mask on the main image canvas to place the contour
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    cv.drawContours(mask, [piece_contour], -1, 255, -1, offset=contour_offset)
    
    # Erode the mask to find a safe inner area
    px, py, pw, ph = cv.boundingRect(piece_contour)
    inset_px = int(min(pw, ph) * 0.15) # Inset by 15% of the piece's smallest dimension
    kernel = np.ones((inset_px, inset_px), np.uint8)
    eroded_mask = cv.erode(mask, kernel, iterations=1)

    # Find the bounding box of the safe area
    contours, _ = cv.findContours(eroded_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(
            f"Warning: Cannot draw label for piece '{piece.name}'. No safe area found after erosion."
        )
        return
    
    if DEBUG:
        # Draw the found contour for the label area
        cv.drawContours(img, contours, -1, DEBUG_CONTOUR_COLOR, 3)

    x, y, w, h = cv.boundingRect(max(contours, key=cv.contourArea))
    # Use distance transform to find the point furthest from any edge.
    # This gives us the safest center point for our label.
    dist_transform = cv.distanceTransform(eroded_mask, cv.DIST_L2, 5)
    
    # Find the point with the maximum distance (the "pole of inaccessibility")
    _, radius, _, center_point_px = cv.minMaxLoc(dist_transform)
    
    if DEBUG:
        # Draw the pole of inaccessibility
        cv.circle(img, center_point_px, 10, DEBUG_POLE_COLOR, -1)
    
    # The radius is the distance to the nearest edge. A square with a side of
    # 2*r/sqrt(2) will fit inside this circle. We can use this to define our
    # bounding box. Let's be slightly more conservative to ensure it fits.
    box_half_width = int(radius / math.sqrt(2) * 0.9)

    # Define the bounding box based on this center and calculated width.
    # center_point_px is (x, y) which is (col, row)
    x = center_point_px[0] - box_half_width
    y = center_point_px[1] - box_half_width
    w = h = int(box_half_width * 2)


    if DEBUG:
        # Draw the bounding box for the text area
        cv.rectangle(img, (x, y), (x + w, y + h), DEBUG_BBOX_COLOR, 2)

    today_str = date.today().strftime("%Y-%m-%d")
    labels = [piece.name, pattern_name, today_str]

    # Dynamically determine font scale
    # Get the size of the longest label at a reference scale of 1.0
    base_text_size, _ = cv.getTextSize(max(labels, key=len), FONT, 1.0, TEXT_THICKNESS)
    
    # Calculate scale based on width and height constraints
    scale_w = w / (base_text_size[0] * 1.25) # adding a bit of a buffer
    # Approximate height for multiple lines
    scale_h = h / (base_text_size[1] * len(labels) * 1.5) 
    font_scale = min(scale_w, scale_h)
    
    line_height = cv.getTextSize(labels[0], FONT, font_scale, TEXT_THICKNESS)[0][1] * 1.5
    # Calculate the total height of the text block
    text_block_height = line_height * (len(labels) - 1) + cv.getTextSize(labels[0], FONT, font_scale, TEXT_THICKNESS)[0][1]
    
    # Calculate the top-most y-coordinate for the first line of text
    start_y_px = y + (h - text_block_height) / 2 + cv.getTextSize(labels[0], FONT, font_scale, TEXT_THICKNESS)[0][1]

    for i, text in enumerate(labels):
        # Calculate the width of the current line of text to center it horizontally
        (text_w, _), _ = cv.getTextSize(text, FONT, font_scale, TEXT_THICKNESS)
        text_x = x + (w - text_w) // 2
        cv.putText(
            img,
            text,
            (text_x, int(start_y_px + i * line_height)),
            FONT,
            font_scale,
            LINE_COLOR,
            TEXT_THICKNESS,
        )

    return font_scale


def _draw_text_along_line(
    img, text, line, piece_offset, scale, color, max_font_scale
):
    """Calculates position and angle, then draws rotated text next to a line."""
    p1_in, p2_in = line.points[0], line.points[1]

    # 1. Calculate line properties
    angle_rad = math.atan2(p2_in[1] - p1_in[1], p2_in[0] - p1_in[0])
    angle_deg = math.degrees(angle_rad)
    line_length_px = math.dist(p1_in, p2_in) * scale
    max_text_length_px = line_length_px * 0.75

    # 2. Estimate text height to calculate perpendicular offset
    temp_font_scale = min(1.0, max_font_scale)
    (_, text_h_estimate), _ = cv.getTextSize(text, FONT, temp_font_scale, TEXT_THICKNESS)
    offset_from_line_px = text_h_estimate * 1.15  # 15% buffer

    # 3. Calculate the final center point for the text
    line_center_x_in = (p1_in[0] + p2_in[0]) / 2
    line_center_y_in = (p1_in[1] + p2_in[1]) / 2

    # Offset the center point perpendicularly from the line
    final_center_x_in = line_center_x_in + (offset_from_line_px / scale) * math.cos(
        angle_rad - math.pi / 2
    )
    final_center_y_in = line_center_y_in + (offset_from_line_px / scale) * math.sin(
        angle_rad - math.pi / 2
    )
    final_center_px = (
        round((final_center_x_in + piece_offset[0]) * scale),
        round((final_center_y_in + piece_offset[1]) * scale),
    )

    # 4. Call the drawing function
    _draw_rotated_text(
        img,
        text,
        final_center_px,
        angle_deg,
        color,
        max_text_length_px,
        max_font_scale,
    )


def _draw_rotated_text(
    img, text, center_px, angle, color, max_length_px, max_font_scale
):
    """Draws rotated text on an image by creating a temporary image and overlaying it."""
    # Determine font scale
    base_text_size_at_1_0_scale, _ = cv.getTextSize(text, FONT, 1.0, TEXT_THICKNESS)
    calculated_font_scale = max_length_px / base_text_size_at_1_0_scale[0]
    font_scale = min(calculated_font_scale, max_font_scale)

    (text_w, text_h), baseline = cv.getTextSize(text, FONT, font_scale, TEXT_THICKNESS)

    # Create a padded, transparent image for the text to prevent clipping during rotation
    padding = int(max(text_w, text_h) * 0.5)
    temp_w, temp_h = text_w + 2 * padding, text_h + 2 * padding
    text_img = np.zeros((temp_h, temp_w, 4), dtype=np.uint8)

    # Draw the text centered in the temporary image
    text_x = padding
    text_y = padding + text_h
    cv.putText(
        text_img,
        text,
        (text_x, text_y),
        FONT,
        font_scale,
        (255, 255, 255, 255),
        TEXT_THICKNESS,
    )

    # Rotate the text image
    rot_center = (temp_w // 2, temp_h // 2)
    rot_mat = cv.getRotationMatrix2D(rot_center, angle, 1.0)

    # Perform the rotation
    rotated_text_img = cv.warpAffine(text_img, rot_mat, (temp_w, temp_h))

    # Calculate top-left corner for placing the rotated text
    x_offset = center_px[0] - (temp_w // 2)
    y_offset = center_px[1] - (temp_h // 2)

    # Overlay the rotated text onto the main image using alpha blending
    for r in range(rotated_text_img.shape[0]):
        for c in range(rotated_text_img.shape[1]):
            if rotated_text_img[r, c, 3] != 0:  # Check alpha channel
                y_pos, x_pos = y_offset + r, x_offset + c
                if 0 <= y_pos < img.shape[0] and 0 <= x_pos < img.shape[1]:
                    alpha = rotated_text_img[r, c, 3] / 255.0
                    img[y_pos, x_pos] = (1 - alpha) * img[
                        y_pos, x_pos
                    ] + alpha * np.array(color, dtype=np.float32)


def draw_lines(img, lines, color, scale=100, offset=(0, 0), thickness=THICKNESS, is_dashed=False):
    for line in lines:
        # Get the final render points, which will be smoothed if the line is smooth.
        render_points = line.get_render_points()
        if render_points: # Apply offset (in inches), scale, and round to integer pixel coordinates
            offset_points = [
                (round((p[0] + offset[0]) * scale), round((p[1] + offset[1]) * scale))
                for p in render_points
            ]

            points_array = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))
            if is_dashed:
                # Simulate dashed lines by drawing short segments
                dash_length = 15
                for i in range(0, len(offset_points) - 1, dash_length * 2):
                    start_idx, end_idx = i, min(i + dash_length, len(offset_points) - 1)
                    if start_idx < end_idx:
                        cv.polylines(img, [points_array[start_idx:end_idx]], isClosed=False, color=color, thickness=thickness)
            else:
                cv.polylines(
                    img, [points_array], isClosed=False, color=color, thickness=thickness
                )
