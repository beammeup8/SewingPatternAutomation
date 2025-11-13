import yaml

class Measurements:
    """A class to hold body measurement data."""

    def __init__(self, **kwargs):
        """
        Initializes the Measurements object.
        
        Args:
            **kwargs: Keyword arguments matching the measurement names.
        """
        # Nested 'shoulders' measurements
        shoulder_specs = kwargs.get('shoulders', {})
        self.shoulders = shoulder_specs.get('full', 0)
        self.shoulder_length = shoulder_specs.get('front shoulder length', 0)
        self.back_shoulder_length = shoulder_specs.get('back shoulder length', 0)
        self.nape_to_shoulder_blade = shoulder_specs.get('nape to shoulder blade', 0)
        self.shoulder_to_armpit = shoulder_specs.get('armscye depth', 0)
        self.side_neck_rise = shoulder_specs.get('side neck rise', 0.5) # Default if not in YAML
        self.shoulder_slope = shoulder_specs.get('shoulder slope', 1.75) # Default if not in YAML
        self.neck_circumference = shoulder_specs.get('neck circumference', 0)

        # Nested 'bust' measurements
        bust_specs = kwargs.get('bust', {})
        self.bust = bust_specs.get('full bust', 0)
        self.upper_bust = bust_specs.get('upper bust', 0)
        self.shoulder_to_bust = bust_specs.get('shoulder to apex', 0)
        self.back_bust_height = bust_specs.get('nape to bust', 0)
        self.front_bust = bust_specs.get('front bust', self.bust / 2)
        self.back_bust = bust_specs.get('back bust', self.bust / 2)
        self.bust_point_separation = bust_specs.get('apex to apex', 0)
        self.across_back = bust_specs.get('back width', self.upper_bust / 2)
        self.across_front = bust_specs.get('front upper bust', self.upper_bust / 2)

        # Nested 'waist' measurements
        waist_specs = kwargs.get('waist', {})
        self.waist = waist_specs.get('full', 0)
        self.shoulder_to_waist = waist_specs.get('nape to waist', 0)

        # Nested 'hip' measurements
        hip_specs = kwargs.get('hip', {})
        self.high_hip = hip_specs.get('high hip', 0)
        self.hip = hip_specs.get('full hip', 0)
        self.waist_to_high_hip = hip_specs.get('waist to high hip', 0)
        self.waist_to_hip = hip_specs.get('waist to hip', 0)

        # Nested 'arm' measurements
        arm_specs = kwargs.get('arm', {})
        self.above_elbow_circumference = arm_specs.get('above_elbow_circumference', 0)
        self.bicep = arm_specs.get('bicep', 0)

    @classmethod
    def from_file(cls, filepath):
        """Loads measurements from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)