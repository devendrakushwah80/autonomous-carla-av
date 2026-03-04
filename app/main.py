import sys
sys.path.append(r"C:\CARLA\CARLA_0.9.16\PythonAPI\carla")
sys.path.append(r"C:\CARLA\CARLA_0.9.16\PythonAPI\carla\agents")

import carla
import cv2
import time
import random
import numpy as np
import math
import psutil

try:
    import GPUtil
    GPU_AVAILABLE = True
except:
    GPU_AVAILABLE = False

from ultralytics import YOLO
from agents.navigation.behavior_agent import BehaviorAgent
from core.simulation.simulator import Simulator
from core.simulation.vehicle_manager import VehicleManager
from core.simulation.sensors import CameraSensor

# ===============================
# YOLO
# ===============================
yolo_model = YOLO("yolov8n.pt")

# ===============================
# CAMERA INTRINSICS
# ===============================
IMG_WIDTH = 480
IMG_HEIGHT = 270
FOV = 90

def get_camera_matrix(width, height, fov):
    focal = width / (2 * np.tan(fov * np.pi / 360))
    K = np.identity(3)
    K[0, 0] = focal
    K[1, 1] = focal
    K[0, 2] = width / 2
    K[1, 2] = height / 2
    return K

K = get_camera_matrix(IMG_WIDTH, IMG_HEIGHT, FOV)

# ===============================
# UTILITIES
# ===============================
def get_speed(vehicle):
    vel = vehicle.get_velocity()
    return 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)

# ===============================
# SAFE SEMANTIC OVERLAY
# ===============================
def add_semantic_overlay(rgb, seg):

    if seg is None:
        return rgb

    if not isinstance(seg, np.ndarray):
        return rgb

    if len(seg.shape) != 3:
        return rgb

    road_color = [128, 64, 128]
    mask = np.all(seg == road_color, axis=2)

    overlay = rgb.copy()
    overlay[mask] = [0, 255, 255]

    return cv2.addWeighted(rgb, 0.85, overlay, 0.4, 0)

# ===============================
# 3D PROJECTION
# ===============================
def project_point(point, ego_transform):

    point = point - ego_transform.location

    # Convert to ego coordinate frame
    forward = ego_transform.get_forward_vector()
    right = ego_transform.get_right_vector()
    up = ego_transform.get_up_vector()

    x = forward.x * point.x + forward.y * point.y + forward.z * point.z
    y = right.x * point.x + right.y * point.y + right.z * point.z
    z = up.x * point.x + up.y * point.y + up.z * point.z

    if x <= 0:
        return None

    pixel = K @ np.array([y, -z, x])
    pixel /= pixel[2]

    return int(pixel[0]), int(pixel[1])


def draw_3d_boxes(world, ego, frame):

    ego_transform = ego.get_transform()
    vehicles = world.get_actors().filter('*vehicle*')

    for vehicle in vehicles:

        if vehicle.id == ego.id:
            continue

        verts = vehicle.bounding_box.get_world_vertices(vehicle.get_transform())

        for vert in verts:
            p = project_point(vert, ego_transform)
            if p:
                cv2.circle(frame, p, 3, (0, 0, 255), -1)

# ===============================
# MAIN
# ===============================
def main():

    print(" Starting Autonomous System...")

    simulator = Simulator()
    world = simulator.get_world()

    vehicle_manager = VehicleManager(world)
    ego = vehicle_manager.spawn_ego()
    vehicle_manager.spawn_npc()

    camera = CameraSensor(world, ego)

    agent = BehaviorAgent(ego, behavior='normal')

    spawn_points = world.get_map().get_spawn_points()
    destination = random.choice(spawn_points).location
    agent.set_destination(destination)

    prev_time = time.time()
    frame_count = 0

    try:
        while True:

            frames = camera.get_frames()
            if frames is None:
                continue

            rgb_frame, seg_frame = frames
            if rgb_frame is None:
                continue

            frame = add_semantic_overlay(rgb_frame, seg_frame)

            # ---------------- YOLO (every 3rd frame)
            if frame_count % 3 == 0:
                results = yolo_model(rgb_frame, imgsz=320, conf=0.4, verbose=False)

                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls = int(box.cls[0])
                        label = yolo_model.names[cls]

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                        cv2.putText(frame, label,
                                    (x1, y1-5),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0,255,0), 2)

            # ---------------- 3D BOXES
            draw_3d_boxes(world, ego, frame)

            # ---------------- AGENT CONTROL
            control = agent.run_step()
            ego.apply_control(control)

            if agent.done():
                destination = random.choice(spawn_points).location
                agent.set_destination(destination)

            # ---------------- PERFORMANCE
            current_time = time.time()
            dt = current_time - prev_time
            prev_time = current_time
            fps = 1.0 / dt if dt > 0 else 0

            cpu = psutil.cpu_percent()

            if GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                gpu_load = gpus[0].load * 100 if gpus else 0
            else:
                gpu_load = 0

            speed = get_speed(ego)

            tl = ego.get_traffic_light()
            tl_state = str(tl.get_state()).split('.')[-1] if tl else "NONE"

            if speed < 1:
                state = "STOPPED"
            elif speed < 20:
                state = "SLOW"
            else:
                state = "CRUISE"

            # ---------------- HUD
            cv2.putText(frame, f"Speed: {speed:.1f} km/h", (10,25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            cv2.putText(frame, f"FPS: {fps:.1f}", (10,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

            cv2.putText(frame, f"CPU: {cpu:.0f}%", (10,75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)

            cv2.putText(frame, f"GPU: {gpu_load:.0f}%", (10,100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)

            cv2.putText(frame, f"Traffic: {tl_state}", (10,125),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

            cv2.putText(frame, f"State: {state}", (10,150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

            display_frame = cv2.resize(frame, (1280, 720))
            cv2.imshow(" Autonomous CARLA - DLCV_Sprinters", display_frame)

            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        print("Cleaning up actors...")
        ego.destroy()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()