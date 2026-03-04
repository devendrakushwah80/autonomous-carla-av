import random
import carla
from configs.config import MAX_NPC

class VehicleManager:

    def __init__(self, world):
        self.world = world
        self.blueprints = world.get_blueprint_library()
        self.ego_vehicle = None
        self.npc_vehicles = []

    def spawn_ego(self):

        blueprint_library = self.world.get_blueprint_library()
        vehicle_bp = blueprint_library.filter('vehicle.*')[0]

        spawn_points = self.world.get_map().get_spawn_points()

        #Pick proper road spawn
        spawn_point = spawn_points[0]

        ego = self.world.spawn_actor(vehicle_bp, spawn_point)

        # Force align with lane waypoint
        waypoint = self.world.get_map().get_waypoint(spawn_point.location)
        ego.set_transform(waypoint.transform)

        return ego

    def spawn_npc(self):
        spawn_points = self.world.get_map().get_spawn_points()
        vehicle_bps = self.blueprints.filter("vehicle.*")

        for _ in range(MAX_NPC):
            bp = random.choice(vehicle_bps)
            spawn = random.choice(spawn_points)
            npc = self.world.try_spawn_actor(bp, spawn)
            if npc:
                npc.set_autopilot(True)
                self.npc_vehicles.append(npc)