import carla
from configs.config import HOST, PORT, TOWN

class Simulator:

    def __init__(self):
        print("Connecting to CARLA...")
        self.client = carla.Client(HOST, PORT)
        self.client.set_timeout(10.0)

        print("Loading world...")
        self.world = self.client.load_world(TOWN)

        print("Setting async mode...")
        self._set_async_mode()

        print("Simulator ready.")

    def _set_async_mode(self):
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = None
        self.world.apply_settings(settings)

    def get_world(self):
        return self.world