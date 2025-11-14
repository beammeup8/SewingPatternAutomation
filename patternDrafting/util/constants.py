import cv2 as cv

# --- Debugging ---
DEBUG = False  # Set to False to disable all debug visualizations
DRAFTING_LINES = False
DRAW_GRID = True # Set to False to hide the 1-inch grid

# --- Drawing Constants ---
# Colors
LINE_COLOR = (255, 255, 255)
BODY_COLOR = (255, 0, 0)
DRAFTING_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (40, 40, 40) # Dark grey for the grid
THICKNESS = 10
TEXT_THICKNESS = THICKNESS // 2
SPACING = 2 # Inches between pattern pieces
FONT = cv.FONT_HERSHEY_SIMPLEX

# Debug Colors
DEBUG_CONTOUR_COLOR = (0, 255, 255)  # Yellow
DEBUG_BBOX_COLOR = (255, 0, 255)     # Magenta
DEBUG_POLE_COLOR = (0, 0, 255)       # Red
