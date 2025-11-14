import yaml
from .necklines import create_neckline

class GarmentSpecs:
    """A class to hold garment specification data."""

    def __init__(self, **kwargs):
        """
        Initializes the GarmentSpecs object.

        Args:
            **kwargs: Keyword arguments matching the garment spec names.
        """
        self.sleeve_length = kwargs.get('sleeve_length', 0)
        self.cuff_ease = kwargs.get('cuff_ease', 0)
        self.waist_to_hem = kwargs.get('waist_to_hem', 0)
        self.bust_ease = kwargs.get('bust_ease', 0)
        self.waist_ease = kwargs.get('waist_ease', 0)
        self.hip_ease = kwargs.get('hip_ease', 0)
        self.seam_allowance = kwargs.get('seam_allowance', 0.5)

        neckline_specs = kwargs.get('neckline', {})
        self.front_neckline_depth = neckline_specs.get('front depth', 0)
        self.back_neckline_depth = neckline_specs.get('back depth', 0)
        self.neckline_radius = neckline_specs.get('radius', 0)

        # Handle single shape or different front/back shapes
        single_shape = neckline_specs.get('shape', 'scoop') # Default if no shapes are specified
        self.front_neckline_shape = neckline_specs.get('front shape', single_shape)
        self.back_neckline_shape = neckline_specs.get('back shape', single_shape)

    def create_bodice_neckline(self, side, shoulder_height):
        """
        Creates the neckline for a given side (Front or Back) by calling the factory.

        Args:
            side (str): "Front" or "Back".
            shoulder_height (float): The y-coordinate of the shoulder line.

        Returns:
            Line: The Line object for the neckline.
        """
        if side == "Front":
            depth_value = self.front_neckline_depth
            shape = self.front_neckline_shape
        elif side == "Back":
            depth_value = self.back_neckline_depth
            shape = self.back_neckline_shape
        else:
            # Fallback for safety, though it shouldn't be reached with current code
            print(f"Warning: Unknown side '{side}' for neckline. Defaulting to back depth.")
            depth_value = self.back_neckline_depth
            shape = self.back_neckline_shape

        # The create_neckline functions expect the y-coordinate at x=0 (center front/back) to be 0.
        return create_neckline(shape, shoulder_height, depth_value, self.neckline_radius), self.neckline_radius

    @classmethod
    def from_file(cls, filepath):
        """Loads garment specs from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)