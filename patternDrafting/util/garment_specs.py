import yaml

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
        self.height_above_hip = kwargs.get('height_above_hip', 0)
        self.front_neckline_depth = kwargs.get('front_neckline_depth', 0)
        self.back_neckline_depth = kwargs.get('back_neckline_depth', 0)
        self.neckline_radius = kwargs.get('neckline_radius', 0)
        self.bust_ease = kwargs.get('bust_ease', 0)
        self.waist_ease = kwargs.get('waist_ease', 0)
        self.hip_ease = kwargs.get('hip_ease', 0)
        self.neckline = kwargs.get('neckline', 'scoop') # Default to 'scoop' if not specified

    @classmethod
    def from_file(cls, filepath):
        """Loads garment specs from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)