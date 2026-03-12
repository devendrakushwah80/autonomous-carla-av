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


# ================= YOLO =================
yolo_model = YOLO("yolov8n.pt")


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


def get_speed(vehicle):
    vel = vehicle.get_velocity()
    return 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)


# ================= SEMANTIC ROAD =================
def add_semantic_overlay(rgb, seg):

    if seg is None:
        return rgb

    road_color = [128, 64, 128]
    mask = np.all(seg == road_color, axis=2)

    overlay = rgb.copy()
    overlay[mask] = [0, 255, 255]

    return cv2.addWeighted(rgb, 0.85, overlay, 0.4, 0)


# ================= 3D PROJECTION =================
def project_point(point, camera_transform):

    point = point - camera_transform.location

    forward = camera_transform.get_forward_vector()
    right = camera_transform.get_right_vector()
    up = camera_transform.get_up_vector()

    x = forward.x * point.x + forward.y * point.y + forward.z * point.z
    y = right.x * point.x + right.y * point.y + right.z * point.z
    z = up.x * point.x + up.y * point.y + up.z * point.z

    if x <= 0:
        return None

    pixel = K @ np.array([y, -z, x])
    pixel /= pixel[2]

    return int(pixel[0]), int(pixel[1])


def draw_box(frame, points):

    edges = [
        (0,1),(1,3),(3,2),(2,0),
        (4,5),(5,7),(7,6),(6,4),
        (0,4),(1,5),(2,6),(3,7)
    ]

    for e in edges:
        if points[e[0]] and points[e[1]]:
            cv2.line(frame, points[e[0]], points[e[1]], (0,0,255), 2)


def draw_3d_box(vehicle, camera, frame):

    camera_transform = camera.rgb_sensor.get_transform()
    verts = vehicle.bounding_box.get_world_vertices(vehicle.get_transform())

    projected = []

    for vert in verts:

        p = project_point(vert, camera_transform)

        if p and 0 <= p[0] < IMG_WIDTH and 0 <= p[1] < IMG_HEIGHT:
            projected.append(p)
        else:
            projected.append(None)

    draw_box(frame, projected)


# ================= MAIN =================
def main():

    print("Starting Autonomous System...")

    simulator = Simulator()
    world = simulator.get_world()

    vehicle_manager = VehicleManager(world, simulator.client)
    ego = vehicle_manager.spawn_ego()
    vehicle_manager.spawn_npc()

    camera = CameraSensor(world, ego)

    agent = BehaviorAgent(ego, behavior='cautious')

    agent.set_target_speed(22)

    spawn_points = world.get_map().get_spawn_points()
    destination = random.choice(spawn_points).location
    agent.set_destination(destination)

    prev_time = time.time()
    frame_count = 0

    try:

        while True:

            rgb_frame, seg_frame, top_frame = camera.get_frames()

            if rgb_frame is None:
                continue

            frame = add_semantic_overlay(rgb_frame, seg_frame)

            vehicles = world.get_actors().filter('*vehicle*')
            camera_loc = camera.rgb_sensor.get_transform().location

            collision_warning = False


            # ================= YOLO =================
            if frame_count % 3 == 0:

                results = yolo_model(rgb_frame, imgsz=320, conf=0.4, verbose=False)

                for r in results:

                    for box in r.boxes:

                        x1,y1,x2,y2 = map(int, box.xyxy[0])
                        label = yolo_model.names[int(box.cls[0])]

                        if label != "car":
                            continue

                        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

                        nearest=None
                        min_dist=999

                        for v in vehicles:

                            if v.id == ego.id:
                                continue

                            dist = camera_loc.distance(v.get_transform().location)

                            if dist < min_dist:
                                min_dist = dist
                                nearest = v

                        if nearest and min_dist < 50:

                            draw_3d_box(nearest,camera,frame)

                            if min_dist < 10:
                                collision_warning = True


            # ================= CONTROL =================
            control = agent.run_step()

            # steering smoothing
            control.steer = np.clip(control.steer, -0.55, 0.55)

            # slow down on turns
            if abs(control.steer) > 0.35:
                control.throttle = min(control.throttle, 0.35)

            # emergency brake
            if collision_warning:
                control.brake = 0.9
                control.throttle = 0

            ego.apply_control(control)


            if agent.done():
                destination = random.choice(spawn_points).location
                agent.set_destination(destination)


            # ================= PERFORMANCE =================
            current_time = time.time()
            fps = 1/(current_time-prev_time)
            prev_time=current_time

            cpu = psutil.cpu_percent()

            gpu_load = 0
            if GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_load = gpus[0].load * 100

            speed = get_speed(ego)

            tl = ego.get_traffic_light()
            tl_state = str(tl.get_state()).split('.')[-1] if tl else "NONE"


            # ================= HUD =================
            cv2.putText(frame,f"Speed: {speed:.1f} km/h",(10,30),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

            cv2.putText(frame,f"FPS: {fps:.1f}",(10,55),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,0),2)

            cv2.putText(frame,f"CPU: {cpu:.0f}%",(10,80),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,255),2)

            cv2.putText(frame,f"GPU: {gpu_load:.0f}%",(10,105),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,255),2)

            cv2.putText(frame,f"Traffic Light: {tl_state}",(10,130),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)

            if collision_warning:
                cv2.putText(frame,"Collision Warning",(10,155),
                            cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)


            # ================= DISPLAY =================
            cv2.imshow("Front Camera",cv2.resize(frame,(1280,720)))

            if top_frame is not None:
                cv2.imshow("Eagle Eye View",cv2.resize(top_frame,(600,400)))

            frame_count+=1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:

        print("Cleaning up actors...")
        ego.destroy()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()