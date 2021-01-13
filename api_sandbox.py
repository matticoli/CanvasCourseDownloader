import os

import canvasapi

API_URL = "https://canvas.wpi.edu"
API_KEY = os.getenv("CANVAS_API_KEY", "NO_API_KEY_SET")

if __name__ == "__main__":
    canvas = canvasapi.Canvas(API_URL, API_KEY)
    print(canvas.get_current_user())
