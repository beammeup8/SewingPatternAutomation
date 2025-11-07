# Drafting loosely following this tutorial

from util.line import Line
from util.pattern_piece import PatternPiece
from util.measurements import Measurements
from util.garment_specs import GarmentSpecs

def _draft_bodice_half(name, measurements, garment_specs, neckline_depth_spec):
  """Drafts a half bodice piece (either front or back)."""
  body_lines = []
  drafting_lines = []
  pattern_lines = []

  # Draw drafting lines
  center_x = 0
  front_top_y = 0

  garm_length = measurements.shoulder_to_waist + measurements.waist_to_hip - garment_specs.height_above_hip
  front_hem_point = front_top_y + garm_length
  neckline_depth = neckline_depth_spec
  neck_point = front_top_y + neckline_depth
  # Center front line (body)
  body_lines.append(Line.vertical(center_x, front_top_y, front_hem_point))
  # Center front line (pattern)
  pattern_lines.append(Line.vertical(center_x, neck_point, front_hem_point))

  # shoulder line
  shoulder_x = center_x + measurements.shoulders/2
  body_lines.append(Line.horizontal(front_top_y, center_x, shoulder_x))

  # neckline
  neckline_line, neckline_radius = garment_specs.create_bodice_neckline(name, front_top_y)
  neckline_outside_x = center_x + neckline_radius
  pattern_lines.append(neckline_line)

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
  
  # Truncate the side seam so it ends at the hemline.
  pattern_lines.append(side_seam_line.truncate_vertical(max_y=front_hem_point))
  pattern_lines.append(hem_line)

  # Assemble the pattern piece
  piece = PatternPiece(name=name,
                       body_lines=body_lines,
                       drafting_lines=drafting_lines,
                       pattern_lines=pattern_lines)
  piece.add_fold_line()
  return piece

def draft(measurements, garment_specs):
  pattern_pieces = []

  # Draft Front Piece
  front_piece = _draft_bodice_half("Front", measurements, garment_specs, garment_specs.front_neckline_depth)
  pattern_pieces.append(front_piece)

  # Draft Back Piece
  back_piece = _draft_bodice_half("Back", measurements, garment_specs, garment_specs.back_neckline_depth)
  pattern_pieces.append(back_piece)
  
  return pattern_pieces

if __name__ == "__main__":
  from util.draw import draw_pattern # Import here as it's only used in __main__
  
  # Load measurements and garment specs from files
  measurements = Measurements.from_file('patternDrafting/measurements/sample_measurements.yaml')
  garment_specs = GarmentSpecs.from_file('patternDrafting/garmentSpecs/sample_garment_specs.yaml')

  pattern_pieces = draft(measurements, garment_specs)
  
  draw_pattern(
      scale=100, # Pixels per inch
      pattern_pieces=pattern_pieces,
      output_filepath="testFiles/batwingDraft.png",
      pattern_name="Batwing Top"
  )
