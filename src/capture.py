import time
import numpy as np
import mss
import cv2
from config import config

# NDI imports
from cyndilib.wrapper.ndi_recv import RecvColorFormat, RecvBandwidth
from cyndilib.finder import Finder
from cyndilib.receiver import Receiver
from cyndilib.video_frame import VideoFrameSync
from cyndilib.audio_frame import AudioFrameSync


def get_region():
    """Center capture region for MSS mode."""
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
        if img.shape[2] == 4:
            img = img[:, :, :3]  # Drop alpha channel
        return img

    def stop(self):
        self.running = False
        self.sct.close()


class NDICamera:
    def __init__(self):
        self.finder = Finder()
        self.finder.set_change_callback(self.on_finder_change)
        self.finder.open()

        self.receiver = Receiver(
            color_format=RecvColorFormat.RGBX_RGBA,
            bandwidth=RecvBandwidth.lowest,
        )
        self.video_frame = VideoFrameSync()
        self.audio_frame = AudioFrameSync()

        self.receiver.frame_sync.set_video_frame(self.video_frame)
        self.receiver.frame_sync.set_audio_frame(self.audio_frame)

        self.connected = False

    def on_finder_change(self):
        sources = self.finder.get_source_names()
        print("[NDI] Found sources:", sources)
        if sources and not self.connected:
            self.connect_to_source(sources[0])

    def connect_to_source(self, source_name):
        with self.finder.notify:
            source = self.finder.get_source(source_name)
        self.receiver.set_source(source)
        if source:
            print(f"[NDI] Connected to {source.name}")
            self.connected = True

    def get_latest_frame(self):
        if not self.receiver.is_connected():
            return None

        self.receiver.frame_sync.capture_video()
        if min(self.video_frame.xres, self.video_frame.yres) == 0:
            return None
        config.ndi_widht, config.ndi_height = self.video_frame.xres, self.video_frame.yres
        # Copy frame to own memory to avoid "cannot write with view active"
        frame = np.frombuffer(self.video_frame, dtype=np.uint8).copy()
        frame = frame.reshape((self.video_frame.yres, self.video_frame.xres, 4))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        return frame

    def stop(self):
        self.finder.close()


def get_camera():
    """Factory function to return the right camera based on config."""
    if config.capturer_mode.lower() == "mss":
        region = get_region()
        cam = MSSCamera(region)
        return cam, region
    elif config.capturer_mode.lower() == "ndi":
        cam = NDICamera()
        return cam, None
    else:
        raise ValueError(f"Unknown capturer_mode: {config.capturer_mode}")
