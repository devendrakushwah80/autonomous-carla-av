import carla
import numpy as np
import threading
from configs.config import IMG_WIDTH, IMG_HEIGHT, FOV


class CameraSensor:

    def __init__(self, world, vehicle):

        self.rgb_frame = None
        self.seg_frame = None
        self.top_frame = None

        # Thread lock
        self.lock = threading.Lock()

        blueprint_library = world.get_blueprint_library()

        # ====================================================
        # RGB FRONT CAMERA (PERCEPTION CAMERA)
        # ====================================================
        rgb_bp = blueprint_library.find("sensor.camera.rgb")
        rgb_bp.set_attribute("image_size_x", str(IMG_WIDTH))
        rgb_bp.set_attribute("image_size_y", str(IMG_HEIGHT))
        rgb_bp.set_attribute("fov", str(FOV))
        rgb_bp.set_attribute("sensor_tick", "0.05")

        front_transform = carla.Transform(
            carla.Location(x=1.5, z=2.4)
        )

        self.rgb_sensor = world.spawn_actor(
            rgb_bp,
            front_transform,
            attach_to=vehicle
        )

        self.rgb_sensor.listen(self._process_rgb)

        # ====================================================
        # SEMANTIC SEGMENTATION CAMERA
        # ====================================================
        seg_bp = blueprint_library.find("sensor.camera.semantic_segmentation")
        seg_bp.set_attribute("image_size_x", str(IMG_WIDTH))
        seg_bp.set_attribute("image_size_y", str(IMG_HEIGHT))
        seg_bp.set_attribute("fov", str(FOV))
        seg_bp.set_attribute("sensor_tick", "0.05")

        self.seg_sensor = world.spawn_actor(
            seg_bp,
            front_transform,
            attach_to=vehicle
        )

        self.seg_sensor.listen(self._process_seg)

        # ====================================================
        # TOP EAGLE CAMERA (DRONE VIEW)
        # ====================================================
        top_bp = blueprint_library.find("sensor.camera.rgb")
        top_bp.set_attribute("image_size_x", str(IMG_WIDTH))
        top_bp.set_attribute("image_size_y", str(IMG_HEIGHT))
        top_bp.set_attribute("fov", "110")
        top_bp.set_attribute("sensor_tick", "0.05")

        top_transform = carla.Transform(
            carla.Location(x=0, z=25),
            carla.Rotation(pitch=-90)
        )

        self.top_sensor = world.spawn_actor(
            top_bp,
            top_transform,
            attach_to=vehicle
        )

        self.top_sensor.listen(self._process_top)

    # ====================================================
    # RGB CALLBACK
    # ====================================================
    def _process_rgb(self, image):

        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((IMG_HEIGHT, IMG_WIDTH, 4))
        frame = array[:, :, :3].copy()

        with self.lock:
            self.rgb_frame = frame

    # ====================================================
    # SEGMENTATION CALLBACK
    # ====================================================
    def _process_seg(self, image):

        image.convert(carla.ColorConverter.CityScapesPalette)

        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((IMG_HEIGHT, IMG_WIDTH, 4))
        frame = array[:, :, :3].copy()

        with self.lock:
            self.seg_frame = frame

    # ====================================================
    # TOP CAMERA CALLBACK
    # ====================================================
    def _process_top(self, image):

        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((IMG_HEIGHT, IMG_WIDTH, 4))
        frame = array[:, :, :3].copy()

        with self.lock:
            self.top_frame = frame

    # ====================================================
    # FRAME GETTER
    # ====================================================
    def get_frames(self):

        with self.lock:

            if self.rgb_frame is None or self.seg_frame is None:
                return None, None, None

            rgb = self.rgb_frame.copy()
            seg = self.seg_frame.copy()

            if self.top_frame is not None:
                top = self.top_frame.copy()
            else:
                top = None

        return rgb, seg, top