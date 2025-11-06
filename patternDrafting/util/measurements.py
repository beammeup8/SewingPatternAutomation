import yaml

class Measurements:
    """A class to hold body measurement data."""

    def __init__(self, **kwargs):
        """
        Initializes the Measurements object.
        
        Args:
            **kwargs: Keyword arguments matching the measurement names.
        """
        self.upper_bust = kwargs.get('upper_bust', 0)
        self.bust = kwargs.get('bust', 0)
        self.waist = kwargs.get('waist', 0)
        self.high_hip = kwargs.get('high_hip', 0)
        self.hip = kwargs.get('hip', 0)
        self.shoulders = kwargs.get('shoulders', 0)
        self.shoulder_to_armpit = kwargs.get('shoulder_to_armpit', 0)
        self.shoulder_to_bust = kwargs.get('shoulder_to_bust', 0)
        self.shoulder_to_waist = kwargs.get('shoulder_to_waist', 0)
        self.waist_to_high_hip = kwargs.get('waist_to_high_hip', 0)
        self.waist_to_hip = kwargs.get('waist_to_hip', 0)
        self.above_elbow_circumference = kwargs.get('above_elbow_circumference', 0)

    @classmethod
    def from_file(cls, filepath):
        """Loads measurements from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)