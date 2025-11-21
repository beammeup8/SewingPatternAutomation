from util.line import Line
from util.dart import Dart
import math
import cv2 as cv
import numpy as np

PADDING_IN = 1  # Inches of padding for temporary masks
LABEL_BUFFER = 0.15 # Percentage of smallest dimension to inset for label placement

class PatternPiece:
  """
  Represents a single piece of a sewing pattern, like a front, back, or sleeve.
  """
  def __init__(self, name, body_lines=None, drafting_lines=None, pattern_lines=None, marking_lines=None):
    """
    Initializes a PatternPiece.

    Args:
      name: The name of the pattern piece (e.g., "Front Bodice").
      body_lines: An optional list of body Line objects.
      drafting_lines: An optional list of drafting Line objects.
      pattern_lines: An optional list of pattern Line objects.
      marking_lines: An optional list of internal marking Line objects (e.g., darts).
    """
    self.name = name
    self.body_lines = body_lines if body_lines is not None else []
    self.drafting_lines = drafting_lines if drafting_lines is not None else []
    self.pattern_lines = pattern_lines if pattern_lines is not None else []
    self.marking_lines = marking_lines if marking_lines is not None else []
    self.cut_lines = []
    self.grainline = None # Will be a tuple of (list[Line], "text")
    self._contour_cache = {}
    self._bounding_box_cache = None

  def get_drawable_marking_lines(self):
      """
      Returns a flat list of all Line objects that should be drawn for markings.
      This handles cases where markings are stored as Dart objects or other structures.
      """
      drawable_lines = []
      for marking in self.marking_lines:
          if isinstance(marking, Line):
              drawable_lines.append(marking)
          elif isinstance(marking, Dart):
              drawable_lines.extend(marking.get_lines())
      return drawable_lines

  def get_marking_by_name(self, name):
      """
      Finds a marking object (Line or Dart) in the marking_lines list by its name.
      """
      for marking in self.marking_lines:
          if hasattr(marking, 'name') and marking.name == name:
              return marking
      return None


  def get_bounding_box(self):
    """
    Calculates the bounding box that encompasses all lines in this piece.
    Returns (min_x, min_y, max_x, max_y) in inches.
    """
    if self._bounding_box_cache:
        return self._bounding_box_cache

    all_points = []
    for line in self.pattern_lines + self.cut_lines:
        # Use get_render_points to account for smoothed curves
        all_points.extend(line.get_render_points())
    
    if not all_points:
        return (0, 0, 0, 0)

    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    
    self._bounding_box_cache = (min_x, min_y, max_x, max_y)
    return self._bounding_box_cache

  def get_outline_contour(self, scale=100):
      """
      Generates a single, continuous contour for the pattern piece's outline
      by drawing it on a temporary mask. Caches the result based on scale.

      Args:
          scale (int): The resolution (pixels per inch) to use for rendering.

      Returns:
          A NumPy array of contour points in pixel coordinates, or None.
      """
      if scale in self._contour_cache:
          return self._contour_cache[scale]

      if not self.pattern_lines:
          return None

      # Create a temporary mask just large enough for this piece
      min_x, min_y, max_x, max_y = self.get_bounding_box()
      width_in = (max_x - min_x) + 2 * PADDING_IN
      height_in = (max_y - min_y) + 2 * PADDING_IN
      
      # The offset to draw the piece within this temporary mask
      temp_offset = (-min_x + PADDING_IN, -min_y + PADDING_IN)

      mask = np.zeros((round(height_in * scale), round(width_in * scale)), dtype=np.uint8)

      # Draw the pattern lines onto the mask to create a solid, connected shape
      from .draw import draw_lines # Local import to avoid circular dependency
      draw_lines(mask, self.pattern_lines, 255, scale=scale, offset=temp_offset, thickness=5)

      # Find and fill the contour
      contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
      cv.drawContours(mask, contours, -1, 255, -1)
      
      result = max(contours, key=cv.contourArea) if contours else None
      self._contour_cache[scale] = result
      return result

  def get_label_box(self, scale=100):
      """
      Calculates the optimal bounding box for placing a label inside the piece.
      This is done by eroding the piece's shape and finding the largest
      inscribed rectangle within the eroded area.

      Args:
          scale (int): The resolution (pixels per inch) to use for rendering.

      Returns:
          A tuple (x, y, w, h) for the bounding box in pixel coordinates,
          and the eroded mask for debug drawing, or None.
      """
      outline_contour = self.get_outline_contour(scale=scale)
      if outline_contour is None:
          return None

      # Create a mask from the contour to perform erosion. This mask is the same
      # size as the one used to generate the contour, ensuring a consistent coordinate system.
      min_x, min_y, max_x, max_y = self.get_bounding_box()
      width_in = (max_x - min_x) + 2 * PADDING_IN
      height_in = (max_y - min_y) + 2 * PADDING_IN
      mask = np.zeros((round(height_in * scale), round(width_in * scale)), dtype=np.uint8)
      cv.drawContours(mask, [outline_contour], -1, 255, -1)

      # Erode the mask to find a safe inner area
      inset_px = int(min(mask.shape) * LABEL_BUFFER) # Inset by a percentage of the smallest dimension
      kernel = np.ones((inset_px, inset_px), np.uint8)
      eroded_mask = cv.erode(mask, kernel, iterations=1)

      # Find the "pole of inaccessibility" to center the label box
      dist_transform = cv.distanceTransform(eroded_mask, cv.DIST_L2, 5)
      _, radius, _, center_point = cv.minMaxLoc(dist_transform)

      if radius == 0:
          return None # No safe area found

      # Calculate the largest square that fits, centered on the pole
      box_half_width = int(radius / math.sqrt(2) * 0.9)

      print(f"Radius: {radius}, Box half width: {box_half_width}")
      print(f"Center point: {center_point}")
      
      # Switch back to piece coordinates
      min_x_in, min_y_in, _, _ = self.get_bounding_box()
      x = (center_point[0] - box_half_width) / scale - PADDING_IN + min_x_in
      y = (center_point[1] - box_half_width) / scale - PADDING_IN + min_y_in
      w = h = (box_half_width * 2) / scale

      return (x, y, w, h, eroded_mask)

  def add_seam_allowance(self, allowance_in, scale=100):
      """
      Generates a seam allowance outline and stores it in `cut_lines`.
      This method creates a temporary image of the pattern piece, dilates it,
      and then converts the resulting contour back into a Line object.

      Args:
          allowance_in (float): The seam allowance in inches.
          scale (int): The resolution (pixels per inch) to use for rendering.
      """
      if not self.pattern_lines:
          return

      # Create a temporary mask to draw the piece and generate the seam allowance.
      min_x, min_y, max_x, max_y = self.get_bounding_box()
      allowance_px = round(allowance_in * scale)
      padding_in = allowance_in * 2
      width_in = (max_x - min_x) + padding_in
      height_in = (max_y - min_y) + padding_in
      temp_offset = (-min_x + allowance_in, -min_y + allowance_in)
      mask = np.zeros((round(height_in * scale), round(width_in * scale)), dtype=np.uint8)

      # Draw the pattern lines onto the mask to create a solid, connected shape.
      from .draw import draw_lines # Local import to avoid circular dependency
      draw_lines(mask, self.pattern_lines, 255, scale=scale, offset=temp_offset, thickness=5)
      contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
      cv.drawContours(mask, contours, -1, 255, -1)

      # Dilate the mask to create the seam allowance.
      dilated_mask = cv.dilate(mask, np.ones((allowance_px, allowance_px), np.uint8), iterations=1)

      # Find the new, larger contour and convert it back to a Line object.
      contours, _ = cv.findContours(dilated_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
      if contours:
          new_contour_px = max(contours, key=cv.contourArea)
          new_points_in = [((p[0][0] / scale) + min_x - allowance_in, (p[0][1] / scale) + min_y - allowance_in) for p in new_contour_px]
          new_line = Line(new_points_in)
          if self.grainline and self.grainline[1] == "CUT ON FOLD":
              new_line.truncate_horizontal(min_x=0)
          self.cut_lines.append(new_line)

  def add_grainline(self, length_in=5, angle=90, arrowhead_length=0.5, arrowhead_angle=25):
      """Adds a standard grainline arrow to the center of the piece."""
      min_x, min_y, max_x, max_y = self.get_bounding_box()
      center_x = (min_x + max_x) / 2
      center_y = (min_y + max_y) / 2

      half_len = length_in / 2
      line_angle_rad = math.radians(angle)

      sx = center_x - half_len * math.cos(line_angle_rad)
      sy = center_y - half_len * math.sin(line_angle_rad)
      ex = center_x + half_len * math.cos(line_angle_rad)
      ey = center_y + half_len * math.sin(line_angle_rad)
      start_point = (sx, sy)
      end_point = (ex, ey)

      # Create points for a single polyline representing the arrow
      arrow_points = [
          (ex - arrowhead_length * math.cos(line_angle_rad - math.radians(arrowhead_angle)), ey - arrowhead_length * math.sin(line_angle_rad - math.radians(arrowhead_angle))),
          end_point,
          (ex - arrowhead_length * math.cos(line_angle_rad + math.radians(arrowhead_angle)), ey - arrowhead_length * math.sin(line_angle_rad + math.radians(arrowhead_angle))),
          end_point,
          start_point,
          (sx + arrowhead_length * math.cos(line_angle_rad - math.radians(arrowhead_angle)), sy + arrowhead_length * math.sin(line_angle_rad - math.radians(arrowhead_angle))),
          start_point,
          (sx + arrowhead_length * math.cos(line_angle_rad + math.radians(arrowhead_angle)), sy + arrowhead_length * math.sin(line_angle_rad + math.radians(arrowhead_angle))),
      ]

      self.grainline = ([Line(arrow_points)], None)

  def add_fold_line(self, margin_in=1, x_coord=0):
      """Adds a 'Cut on Fold' indicator along the center front (x=0)."""
      # Find the min and max Y of the center front line from the pattern lines
      cf_points = [p for line in self.pattern_lines for p in line.get_render_points() if p[0] == x_coord]
      if not cf_points:
          print("Warning: Could not add fold line. No line found at x={x_coord}.")
          return

      min_y = min(p[1] for p in cf_points)
      max_y = max(p[1] for p in cf_points)

      line_x = margin_in
      shaft = Line([(line_x, min_y + margin_in), (line_x, max_y - margin_in)])
      top_y = min_y + margin_in
      bottom_y = max_y - margin_in
      top_t = Line([(line_x - margin_in, top_y), (line_x, top_y)])
      bottom_t = Line([(line_x - margin_in, bottom_y), (line_x, bottom_y)])

      self.grainline = ([shaft, top_t, bottom_t], "CUT ON FOLD")

  def true_dart(self, dart_legs, is_waist_dart=False):
      """
      Adjusts the cut line to 'true' a dart, adding a dart cap or dipping the hem.
      This ensures seam lines match up after the dart is sewn.
      """
      if not self.cut_lines or not dart_legs:
          return

      cut_line = self.cut_lines[0]
      dart_tip = dart_legs[0].points[1]
      leg1_start = dart_legs[0].points[0]
      leg2_start = dart_legs[1].points[0]

      # Find the points on the cut line that correspond to the dart legs.
      # This is a simplification; a full intersection algorithm would be more robust.
      # For now, we find the closest points on the cut line.
      cut_points = cut_line.get_render_points()
      if not cut_points:
          return

      try:
          idx1 = min(range(len(cut_points)), key=lambda i: math.dist(cut_points[i], leg1_start))
          idx2 = min(range(len(cut_points)), key=lambda i: math.dist(cut_points[i], leg2_start))
      except ValueError:
          return # No points on cut line

      start_idx, end_idx = min(idx1, idx2), max(idx1, idx2)

      if is_waist_dart:
          # Dip the hemline to true the waist dart
          dart_width = math.dist(leg1_start, leg2_start)
          dip_depth = dart_width * 0.25  # Heuristic for dip amount
          mid_idx = (start_idx + end_idx) // 2
          if mid_idx < len(cut_points):
              original_point = cut_points[mid_idx]
              dipped_point = (original_point[0], original_point[1] + dip_depth)
              new_cut_points = cut_points[:mid_idx] + [dipped_point] + cut_points[mid_idx+1:]
              self.cut_lines[0] = Line(new_cut_points, smooth=True)
      else: # Side seam dart
          # Add a dart cap to true the side seam dart
          dart_midpoint_on_seam = ((leg1_start[0] + leg2_start[0]) / 2, (leg1_start[1] + leg2_start[1]) / 2)
          vx = dart_midpoint_on_seam[0] - dart_tip[0] # Vector from dart tip to midpoint on seam
          vy = dart_midpoint_on_seam[1] - dart_tip[1]
          cap_point = (dart_midpoint_on_seam[0] + vx * 0.1, dart_midpoint_on_seam[1] + vy * 0.1) # Project a point outwards
          new_cut_points = cut_points[:start_idx+1] + [cap_point] + cut_points[end_idx:]
          self.cut_lines[0] = Line(new_cut_points, smooth=True)
