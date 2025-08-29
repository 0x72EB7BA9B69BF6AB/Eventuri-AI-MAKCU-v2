
from ultralytics import YOLO
import os
from core.config import config
import torch

_model = None
_class_names = {}
if torch.cuda.is_available():
    DEVICE = 0               
else:
    DEVICE = "cpu"
def load_model(model_path=None):
    global _model, _class_names
    if model_path is None:
        model_path = config.model_path
    try:
        _model = YOLO(model_path, task="detect")
        # Get class names
        if hasattr(_model, "names"):
            _class_names = _model.names
        elif hasattr(_model.model, "names"):
            _class_names = _model.model.names
        else:
            _class_names = {}
            config.model_load_error = "Class names not found"
        # Save available classes and model size
        config.model_classes = list(_class_names.values())
        config.model_file_size = os.path.getsize(model_path) if os.path.exists(model_path) else 0
        config.model_load_error = ""
        return _model, _class_names
    except Exception as e:
        config.model_load_error = f"Failed to load model: {e}"
        _model = None
        _class_names = {}
        return None, {}

def reload_model(model_path):
    return load_model(model_path)

def perform_detection(model, image):
    results = model.predict(
        source=image,
        imgsz=config.imgsz,
        stream=True,
        conf=config.conf,
        iou=0.5,
        device=DEVICE,
        half=True,
        max_det=config.max_detect,
        agnostic_nms=False,
        augment=False,
        vid_stride=False,
        visualize=False,
        verbose=False,
        show_boxes=False,
        show_labels=False,
        show_conf=False,
        save=False,
        show=False
    )
    return results

def get_class_names():
    return _class_names

def get_model_size(model_path=None):
    if not model_path:
        model_path = config.model_path
    return os.path.getsize(model_path) if os.path.exists(model_path) else 0
