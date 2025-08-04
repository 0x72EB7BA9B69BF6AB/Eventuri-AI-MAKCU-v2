import mss
import numpy as np
from config import config

def get_region():
    # Capture the region as originally intended
    left = (config.screen_width - config.region_size) // 2
    top = (config.screen_height - config.region_size) // 2
    right = left + config.region_size
    bottom = top + config.region_size
    return (left, top, right, bottom)

class MSSCamera:
    def __init__(self, region):
        self.region = region
        self.sct = mss.mss()
        self.monitor = {
            "top": region[1],
            "left": region[0],
            "width": region[2] - region[0],
            "height": region[3] - region[1],
        }
        self.running = True
    def get_latest_frame(self):
        img = np.array(self.sct.grab(self.monitor))
        # Remove alpha channel if present
        if img.shape[2] == 4:
            img = img[:, :, :3]
        return img
    def stop(self):
        self.running = False
        self.sct.close()

def get_camera():
    region = get_region()
    cam = MSSCamera(region)
    return cam, region
