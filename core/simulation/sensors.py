import carla
import numpy as np
from configs.config import IMG_WIDTH, IMG_HEIGHT, FOV


class CameraSensor:

    def __init__(self, world, vehicle):

        self.rgb_frame = None
        self.seg_frame = None

        blueprint_library = world.get_blueprint_library()

        # RGB camera
        rgb_bp = blueprint_library.find("sensor.camera.rgb")
        rgb_bp.set_attribute("image_size_x", str(IMG_WIDTH))
        rgb_bp.set_attribute("image_size_y", str(IMG_HEIGHT))
        rgb_bp.set_attribute("fov", str(FOV))

        # Semantic camera
        seg_bp = blueprint_library.find("sensor.camera.semantic_segmentation")
        seg_bp.set_attribute("image_size_x", str(IMG_WIDTH))
        seg_bp.set_attribute("image_size_y", str(IMG_HEIGHT))
        seg_bp.set_attribute("fov", str(FOV))

        transform = carla.Transform(
            carla.Location(x=1.5, z=2.4)
        )

        self.rgb_sensor = world.spawn_actor(rgb_bp, transform, attach_to=vehicle)
        self.seg_sensor = world.spawn_actor(seg_bp, transform, attach_to=vehicle)

        self.rgb_sensor.listen(self._process_rgb)
        self.seg_sensor.listen(self._process_seg)

    def _process_rgb(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((IMG_HEIGHT, IMG_WIDTH, 4))
        self.rgb_frame = array[:, :, :3].copy()

    def _process_seg(self, image):
        image.convert(carla.ColorConverter.CityScapesPalette)
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((IMG_HEIGHT, IMG_WIDTH, 4))
        self.seg_frame = array[:, :, :3].copy()

    def get_frames(self):
        return self.rgb_frame, self.seg_frame