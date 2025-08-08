import numpy as np
import time
import threading
from mouse import Mouse, is_button_pressed  # Use the thread-safe function
from capture import get_camera
from detection import load_model, perform_detection
from config import config
from windmouse_smooth import smooth_aimer
import os
import math
import cv2
import queue

# --- Global state for aimbot control ---
_aimbot_running = False
_aimbot_thread = None
_capture_thread = None
_smooth_thread = None
fps = 0
frame_queue = queue.Queue(maxsize=1)
smooth_move_queue = queue.Queue(maxsize=10)  # Queue for smooth movements
makcu = None  # <-- Declare Mouse instance globally, will be initialized once

def smooth_movement_loop():
    """
    Dedicated thread for executing smooth movements.
    This ensures movements are executed with precise timing.
    """
    global _aimbot_running, makcu
    print("[INFO] Smooth movement thread started")
    while _aimbot_running:
        try:
            # Get next movement from queue (blocking with timeout)
            move_data = smooth_move_queue.get(timeout=0.1)
            dx, dy, delay = move_data


            # Execute the movement
            makcu.move(dx, dy)

            # Wait for the specified delay
            if delay > 0:
                time.sleep(delay)

        except queue.Empty:
            # No movements in queue, continue
            continue
        except Exception as e:
            print(f"[ERROR] Smooth movement failed: {e}")
            time.sleep(0.01)

    print("[INFO] Smooth movement thread stopped")

def capture_loop():
    """PRODUCER: This loop runs on a dedicated CPU thread."""
    camera, _ = get_camera()  # Create camera instance inside the thread
    while _aimbot_running:
        try:
            image = camera.get_latest_frame()
            if image is not None:
                try:
                    frame_queue.put(image, block=False)
                except queue.Full:
                    try:
                        frame_queue.get_nowait()  # Drop old frame
                    except queue.Empty:
                        pass
                    try:
                        frame_queue.put(image, block=False)
                    except queue.Full:
                        pass  # Extremely rare, ignore
        except Exception as e:
            print(f"[ERROR] Capture loop failed: {e}")
            time.sleep(1)  # Prevent spamming errors
    try:
        camera.stop()
    except Exception as e:
        print(f"[ERROR] Camera stop failed: {e}")
    print("[INFO] Capture loop stopped.")

def detection_and_aim_loop():
    """CONSUMER: This loop runs on the main aimbot thread, utilizing the GPU."""
    global _aimbot_running, fps, makcu
    model, class_names = load_model(config.model_path)
    # makcu is already initialized in start_aimbot


    frame_count = 0
    start_time = time.perf_counter()  # Use a more precise clock
    debug_window_moved = False  # Track if debug window has been moved

    while _aimbot_running:
        try:
            image = frame_queue.get(timeout=1)
        except queue.Empty:
            print("[WARN] Frame queue is empty. Capture thread may have stalled.")
            continue
        if config.capturer_mode.lower() == "mss":
            region_left = (config.screen_width - config.region_size) // 2
            region_top  = (config.screen_height - config.region_size) // 2
            crosshair_x = config.screen_width // 2
            crosshair_y = config.screen_height // 2
        else:
            region_left = (config.screen_width - config.ndi_widht) // 2
            region_top  = (config.screen_height - config.ndi_height) // 2
            crosshair_x = config.screen_width // 2
            crosshair_y = config.screen_height // 2
        
        all_targets = []
        if config.capturer_mode.lower() == "ndi":
            image = cv2.resize(image, (config.ndi_widht, config.ndi_height))
        debug_image = image.copy() if config.show_debug_window else None
        detected_classes = set()  # Track what classes are being detected

        results = perform_detection(model, image)

        # --- Target Processing Logic ---
        if results:
            for result in results:
                if result.boxes is None: continue
                for box in result.boxes:
                    coords = [val.item() for val in box.xyxy[0]]
                    if any(math.isnan(c) for c in coords):
                        print("[WARN] Skipping box with NaN coords:", coords)
                        continue

                    x1, y1, x2, y2 = [int(c) for c in coords]
                    conf = float(box.conf[0].item())
                    cls = int(box.cls[0].item())
                    class_name = class_names.get(cls, f"class_{cls}")

                    # Debug: Track all detected classes
                    detected_classes.add(class_name)



                    # Check if this detection should be a target
                    is_target = False
                    target_type = "unknown"

                    # Handle both string class names and numeric IDs
                    player_label = config.custom_player_label
                    head_label = config.custom_head_label

                    # Convert to string for comparison if needed
                    class_name_str = str(class_name)
                    player_label_str = str(player_label) if player_label is not None else None
                    head_label_str = str(head_label) if head_label is not None else None

                    # Check for exact matches (both string and numeric)
                    if class_name_str == player_label_str:
                        is_target = True
                        target_type = "player"
                    elif head_label_str and class_name_str == head_label_str:
                        is_target = True
                        target_type = "head"
                    # Also check if the class ID matches directly
                    elif str(cls) == player_label_str:
                        is_target = True
                        target_type = "player"
                    elif head_label_str and str(cls) == head_label_str:
                        is_target = True
                        target_type = "head"
                    # Fallback: partial string matching for text classes
                    elif player_label_str and len(player_label_str) > 1:  # Only for non-numeric
                        if not player_label_str.isdigit() and player_label_str.lower() in class_name_str.lower():
                            is_target = True
                            target_type = "player"
                            print(f"[DEBUG] Partial match for player: '{class_name}' contains '{player_label}'")
                    elif head_label_str and len(head_label_str) > 1:  # Only for non-numeric
                        if not head_label_str.isdigit() and head_label_str.lower() in class_name_str.lower():
                            is_target = True
                            target_type = "head"
                            print(f"[DEBUG] Partial match for head: '{class_name}' contains '{head_label}'")

                    if is_target:
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2

                        # Adjust for headshot
                        if target_type == "player":
                            center_x = (x1 + x2) / 2
                            center_y = y1 + config.player_y_offset

                        # Calculate distance from crosshair
                        if config.capturer_mode.lower() == "mss":
                            dist = math.hypot(center_x - (config.region_size / 2), center_y - (config.region_size / 2))
                        else:
                            dist = math.hypot(center_x - (config.ndi_widht / 2), center_y - (config.ndi_height / 2))
                        all_targets.append({
                            'dist': dist, 
                            'center_x': center_x, 
                            'center_y': center_y,
                            'type': target_type,
                            'class': class_name,
                            'conf': conf
                        })

                        

                    # Draw debug boxes
                    if debug_image is not None:
                        if is_target:
                            # Green for player, red for head
                            color = (0, 255, 0) if target_type == "player" else (0, 0, 255)
                            thickness = 3
                        else:
                            # Yellow for non-targets
                            color = (0, 255, 255)
                            thickness = 1

                        cv2.rectangle(debug_image, (x1, y1), (x2, y2), color, thickness)

                        # Label with class name and confidence
                        label = f"{class_name} {conf:.2f}"
                        if is_target:
                            label += f" [{target_type.upper()}]"

                        cv2.putText(debug_image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # --- Target Selection and Aiming (Only when button is held) ---
        button_held = is_button_pressed(config.selected_mouse_button)
        if all_targets and button_held:
            best_target = min(all_targets, key=lambda t: t['dist'])

            target_screen_x = region_left + best_target['center_x']
            target_screen_y = region_top + best_target['center_y']

            dx = target_screen_x - crosshair_x
            dy = target_screen_y - crosshair_y

            # Apply im-game-sensitivity scaling
            sens = config.in_game_sens
            distance = 1.07437623 * math.pow(sens, -0.9936827126)
            # Apply distance scaling
            dx *= distance
            dy *= distance


           
            if config.mode == "normal":
                # Apply x,y speeds scaling
                dx *= config.normal_x_speed
                dy *= config.normal_y_speed
                makcu.move(dx, dy)
            elif config.mode == "bezier":
                makcu.move_bezier(dx, dy, config.bezier_segments, config.bezier_ctrl_x, config.bezier_ctrl_y)
            elif config.mode == "silent":
                makcu.move_bezier(dx, dy, config.silent_segments, config.silent_ctrl_x, config.silent_ctrl_y)
            elif config.mode == "smooth":
                # Use smooth aiming with WindMouse algorithm
                
                path = smooth_aimer.calculate_smooth_path(dx, dy, config)



                # Add all movements to the smooth movement queue
                movements_added = 0
                for move_dx, move_dy, delay in path:
                    if not smooth_move_queue.full():
                        smooth_move_queue.put((move_dx, move_dy, delay))
                        movements_added += 1
                        if movements_added <= 3:  # Only print first few to avoid spam
                            print(f"[DEBUG] Added movement: ({move_dx}, {move_dy}) with delay {delay:.3f}")
                    else:
                        # If queue is full, clear it and add this movement
                        print("[DEBUG] Queue full, clearing and adding movement")
                        try:
                            while not smooth_move_queue.empty():
                                smooth_move_queue.get_nowait()
                        except queue.Empty:
                            pass
                        smooth_move_queue.put((move_dx, move_dy, delay))
                        movements_added += 1
                        break

                print(f"[DEBUG] Added {movements_added} movements to queue")

                # Fallback: if no smooth movements generated, use direct movement
                if len(path) == 0:
                    print("[DEBUG] No smooth path generated, using direct movement")
                    makcu.move(dx, dy)
        else:
            # Reset fatigue when not aiming
            smooth_aimer.reset_fatigue()

        # --- Debug Window Display ---
        if debug_image is not None:
            # Add overlays (same as before)
            button_held = is_button_pressed(config.selected_mouse_button)
            status_text = f"Button {config.selected_mouse_button}: {'HELD' if button_held else 'released'}"
            color = (0, 255, 0) if button_held else (0, 0, 255)
            cv2.putText(debug_image, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            target_text = f"Targets: {len(all_targets)} | Detected: {len(detected_classes)} classes"
            cv2.putText(debug_image, target_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            settings_text = f"Looking for: '{config.custom_player_label}', '{config.custom_head_label}'"
            cv2.putText(debug_image, settings_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            mode_text = f"Mode: {config.mode.upper()}"
            cv2.putText(debug_image, mode_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            if config.mode == "smooth":
                queue_text = f"Smooth Queue: {smooth_move_queue.qsize()}/10"
                cv2.putText(debug_image, queue_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            if detected_classes:
                classes_text = f"Classes: {', '.join(sorted(detected_classes))}"
                cv2.putText(debug_image, classes_text, (10, debug_image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

            # Draw crosshair
            if config.capturer_mode.lower() == "mss":
                center = (config.region_size // 2, config.region_size // 2)
            else:
                center = (config.ndi_widht // 2, config.ndi_height // 2)

            cv2.drawMarker(debug_image, center, (255, 255, 255), cv2.MARKER_CROSS, 20, 2)

            # Show window in center of screen
            win_name = "AI Debug"
            cv2.imshow(win_name, debug_image)

            # Calculate center position
            if not debug_window_moved:
                screen_w, screen_h = config.screen_width, config.screen_height
                win_w, win_h = debug_image.shape[1], debug_image.shape[0]
                x = (screen_w - win_w) // 2
                y = (screen_h - win_h) // 2
                cv2.moveWindow(win_name, x, y)
                debug_window_moved = True 
            cv2.waitKey(1)


        # --- FPS Calculation ---
        frame_count += 1
        elapsed = time.perf_counter() - start_time
        if elapsed > 1.0:
            fps = frame_count / elapsed
            start_time = time.perf_counter()
            frame_count = 0

def start_aimbot():
    global _aimbot_running, _aimbot_thread, _capture_thread, _smooth_thread, makcu
    if _aimbot_running:
        return
    try:
        if makcu is None:  # <-- Initialize only once
            Mouse.cleanup()
            makcu=Mouse()
    except Exception as e:
        print(f"[ERROR] Failed to cleanup Mouse instance: {e}")

    _aimbot_running = True

    # Start capture thread
    _capture_thread = threading.Thread(target=capture_loop, daemon=True)
    _capture_thread.start()

    # Start smooth movement thread (for smooth mode)
    _smooth_thread = threading.Thread(target=smooth_movement_loop, daemon=True)
    _smooth_thread.start()

    # Start main detection thread
    _aimbot_thread = threading.Thread(target=detection_and_aim_loop, daemon=True)
    _aimbot_thread.start()

    button_names = ["Left", "Right", "Middle", "Side 4", "Side 5"]
    button_name = button_names[config.selected_mouse_button] if config.selected_mouse_button < len(button_names) else f"Button {config.selected_mouse_button}"
    print(f"[INFO] Aimbot started in {config.mode} mode. Hold {button_name} button to aim.")

def stop_aimbot():
    global _aimbot_running
    _aimbot_running = False
    try:
        if makcu is None:  # <-- Initialize only once
            Mouse.cleanup()
    except Exception as e:
        print(f"[ERROR] Failed to cleanup Mouse instance: {e}")
    # Clear the smooth movement queue
    try:
        while not smooth_move_queue.empty():
            smooth_move_queue.get_nowait()
    except queue.Empty:
        pass

    if config.show_debug_window:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass  # Ignore errors if window was already closed
    print("[INFO] Aimbot stopped.")

def is_aimbot_running():
    return _aimbot_running

# Rest of the utility functions remain the same
def reload_model(path=None):
    if path is None: path = config.model_path
    return load_model(path)

def get_model_classes(path=None):
    if path is None: path = config.model_path
    _, class_names = load_model(path)
    return [class_names[i] for i in sorted(class_names.keys())]

def get_model_size(path=None):
    if path is None: path = config.model_path
    try:
        return f"{os.path.getsize(path) / (1024*1024):.2f} MB"
    except Exception:
        return "?"

__all__ = [
    'start_aimbot', 'stop_aimbot', 'is_aimbot_running', 'reload_model',
    'get_model_classes', 'get_model_size', 'fps'
]
