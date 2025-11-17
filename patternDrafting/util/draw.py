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
    # Get the label bounding box from the piece itself
    label_box_data = piece.get_label_box(scale=scale)
    if label_box_data is None:
        print(
            f"Warning: Cannot draw label for piece '{piece.name}'. No safe area found after erosion."
        )
        return
    x_in, y_in, w_in, h_in, eroded_mask = label_box_data

    # Apply the piece's layout offset to the label coordinates
    x = round((x_in + offset[0]) * scale) 
    y = round((y_in + offset[1]) * scale) 
    w = round(w_in * scale)
    h = round(h_in * scale)

    print(f"Drawing label for piece '{piece.name}' at ({x}, {y}) with size ({w}, {h}).")
    print(f"Original label box: ({x_in}, {y_in}, {w_in}, {h_in})")
    print(f"Offset: {offset}")

    if DEBUG:
        # Draw the debug visualizations
        piece_contour = piece.get_outline_contour(scale=scale)
        min_x_in, min_y_in, _, _ = piece.get_bounding_box()
        
        # Calculate the absolute offset for drawing debug contours on the main canvas
        abs_contour_offset = (round((offset[0] + min_x_in - 1) * scale), round((offset[1] + min_y_in - 1) * scale))
        
        # Draw the main outline contour
        cv.drawContours(img, [piece_contour], -1, (0, 165, 255), 2, offset=abs_contour_offset)

        # Draw the eroded contour
        # The eroded mask is relative to the temporary mask inside get_label_box.
        # To place it correctly, we need to find the origin of that temporary mask on the final canvas.
        eroded_contours, _ = cv.findContours(eroded_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        eroded_origin_on_canvas = (round((offset[0] + min_x_in - 1) * scale), round((offset[1] + min_y_in - 1) * scale))
        cv.drawContours(img, eroded_contours, -1, DEBUG_CONTOUR_COLOR, 3, offset=eroded_origin_on_canvas)
        
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


def _draw_dashed_polyline(img, points, color, thickness):
    """Draws a dashed polyline by iterating through segments and tracking distance."""
    dash_length = 15
    gap_length = 15
    total_length = dash_length + gap_length
    dist_along_path = 0

    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i+1]
        segment_len = math.dist(p1, p2)
        
        if segment_len == 0:
            continue

        # Vector for the current segment
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        
        # Current position along the segment
        current_pos_on_segment = 0

        while current_pos_on_segment < segment_len:
            # Determine if we are in a dash or a gap
            is_in_dash = (dist_along_path % total_length) < dash_length
            
            # Find the distance to the end of the current phase (dash or gap)
            remaining_in_phase = dash_length - (dist_along_path % total_length) if is_in_dash else total_length - (dist_along_path % total_length)
            
            # Distance to move is the smaller of remaining phase or remaining segment
            dist_to_end_of_segment = segment_len - current_pos_on_segment
            step = min(remaining_in_phase, dist_to_end_of_segment)

            if is_in_dash:
                start_draw_point = (int(p1[0] + (current_pos_on_segment / segment_len) * dx), int(p1[1] + (current_pos_on_segment / segment_len) * dy))
                end_draw_point = (int(p1[0] + ((current_pos_on_segment + step) / segment_len) * dx), int(p1[1] + ((current_pos_on_segment + step) / segment_len) * dy))
                cv.line(img, start_draw_point, end_draw_point, color, thickness)

            dist_along_path += step
            current_pos_on_segment += step

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
                _draw_dashed_polyline(img, offset_points, color, thickness)
            else:
                cv.polylines(
                    img, [points_array], isClosed=False, color=color, thickness=thickness
                )
