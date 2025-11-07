# Drafting loosely following this tutorial

from necklines import *
from util.line import Line
from util.pattern_piece import PatternPiece
from util.measurements import Measurements
from util.garment_specs import GarmentSpecs

SCALE = 100
BOARDER = 2

def draft(measurements, garment_specs):
  # Dimensions in inches
  total_x_in = 25
  total_y_in = 30
  body_lines = []
  drafting_lines = []
  pattern_lines = []

  spacing = BOARDER

  # Draw drafting lines
  center_x = 0
  front_top_y = 0

  garm_length = measurements.shoulder_to_waist + measurements.waist_to_hip - garment_specs.height_above_hip
  front_hem_point = front_top_y + garm_length
  front_neckline_depth = garment_specs.front_neckline_depth
  front_neck_point = front_top_y + front_neckline_depth
  # Center front line (body)
  body_lines.append(Line.vertical(center_x, front_top_y, front_hem_point))
  # Center front line (pattern)
  pattern_lines.append(Line.vertical(center_x, front_neck_point, front_hem_point))

  # shoulder line
  shoulder_x = center_x + measurements.shoulders/2
  body_lines.append(Line.horizontal(front_top_y, center_x, shoulder_x))

  # neckline
  neckline_radius = garment_specs.neckline_radius
  
  # This is currently drawing all three neckline options on top of each other.
  # You can comment out the ones you don't want to see.
  
  # Square neckline 
  pattern_lines.append(create_square_neckline(front_top_y, front_neck_point, neckline_radius))
  # V-neckline 
  pattern_lines.append(create_v_neckline(front_top_y, front_neck_point, neckline_radius))
  # Scoop neckline 
  pattern_lines.append(create_scoop_neckline(front_top_y, front_neck_point, neckline_radius))

  # upper bust line
  upper_bust_x = center_x + measurements.upper_bust/4
  upper_bust_y = front_top_y + measurements.shoulder_to_armpit
  body_lines.append(Line.horizontal(upper_bust_y, center_x, upper_bust_x))
  
  # bust line
  bust_x = center_x + measurements.bust/4
  bust_y = front_top_y + measurements.shoulder_to_bust
  body_lines.append(Line.horizontal(bust_y, center_x, bust_x))

  # waist line
  waist_x = center_x + measurements.waist/4
  waist_y = front_top_y + measurements.shoulder_to_waist
  body_lines.append(Line.horizontal(waist_y, center_x, waist_x))

  # high hip line
  high_hip_x = center_x + measurements.high_hip/4
  high_hip_y = front_top_y + measurements.shoulder_to_waist + measurements.waist_to_high_hip
  body_lines.append(Line.horizontal(high_hip_y, center_x, high_hip_x))

  # hip line
  hip_x = center_x + measurements.hip/4
  hip_y = front_top_y + measurements.shoulder_to_waist + measurements.waist_to_hip
  body_lines.append(Line.horizontal(hip_y, center_x, hip_x))

  # Sleeve Lines
  sleeve_edge_x = center_x + garment_specs.sleeve_length + measurements.shoulders/2
  armpit_depth = measurements.shoulder_to_bust
  sleeve_edge_y = (front_top_y + armpit_depth)/2
  drafting_lines.append(Line.horizontal(sleeve_edge_y, center_x, sleeve_edge_x))

  neckline_outside_x = center_x + neckline_radius
  pattern_lines.append(Line.horizontal(front_top_y, neckline_outside_x, shoulder_x))

  sleeve_width = garment_specs.cuff_ease + measurements.above_elbow_circumference
  cuff_top_y = sleeve_edge_y - sleeve_width/4
  cuff_bottom_y = sleeve_edge_y + sleeve_width/4
  pattern_lines.append(Line.vertical(sleeve_edge_x, cuff_top_y, cuff_bottom_y))

  pattern_lines.append(Line([(shoulder_x, front_top_y), (sleeve_edge_x, cuff_top_y)]))

  # Body Curve
  body_lines.append(Line([(upper_bust_x, upper_bust_y), (bust_x, bust_y), (waist_x, waist_y), (high_hip_x, high_hip_y), (hip_x, hip_y)], smooth=True))

  bust_ease = garment_specs.bust_ease/4
  waist_ease = garment_specs.waist_ease/4
  hip_ease = garment_specs.hip_ease/4

  side_seam_line = Line([(sleeve_edge_x, cuff_bottom_y), (bust_x + bust_ease, bust_y), (waist_x + waist_ease, waist_y), (high_hip_x + hip_ease, high_hip_y), (hip_x + hip_ease, hip_y)], smooth=True)
  hem_line = Line([(center_x, front_hem_point), (hip_x + hip_ease, front_hem_point)])
  
  # The intersection logic has been removed. Adding the full lines for now.
  pattern_lines.append(side_seam_line)
  pattern_lines.append(hem_line)

  # Define layout offsets
  front_offset_in = (spacing, spacing)

  # Assemble the pattern pieces at the end
  front_piece = PatternPiece(name="Front",
                             offset_in=front_offset_in,
                             body_lines=body_lines,
                             drafting_lines=drafting_lines,
                             pattern_lines=pattern_lines)

  # Add grainline or fold line indicator
  front_piece.add_fold_line()

  # The back piece drafting would go here
  # back_offset_in = (spacing, front_offset_in[1] + front_hem_point + spacing)
  # back_piece = PatternPiece(name="Back", offset_in=back_offset_in)
  
  return {
      'pattern_pieces': [front_piece],
      'canvas_size': (total_x_in, total_y_in)
  }

if __name__ == "__main__":
  from util.draw import draw_pattern # Import here as it's only used in __main__
  
  # Load measurements and garment specs from files
  measurements = Measurements.from_file('patternDrafting/measurements/sample_measurements.yaml')
  garment_specs = GarmentSpecs.from_file('patternDrafting/garmentSpecs/sample_garment_specs.yaml')

  pattern_data = draft(measurements, garment_specs)
  
  draw_pattern(
      canvas_size_in=pattern_data['canvas_size'],
      scale=SCALE,
      pattern_pieces=pattern_data['pattern_pieces'],
      output_filepath="testFiles/batwingDraft.png",
      pattern_name="Batwing Top"
  )

  print(pattern_data['canvas_size'])
