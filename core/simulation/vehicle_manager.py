import random
import carla
from configs.config import MAX_NPC


class VehicleManager:

    def __init__(self, world, client):

        self.world = world
        self.client = client
        self.blueprints = world.get_blueprint_library()
        self.ego_vehicle = None
        self.npc_vehicles = []

        # Traffic Manager
        self.tm = self.client.get_trafficmanager(8000)
        self.tm.set_global_distance_to_leading_vehicle(3.0)
        self.tm.set_synchronous_mode(False)


    # ==================================================
    # SPAWN EGO VEHICLE
    # ==================================================
    def spawn_ego(self):

        vehicle_bp = self.blueprints.filter("vehicle.tesla.model3")[0]

        spawn_points = self.world.get_map().get_spawn_points()

        spawn_point = random.choice(spawn_points)

        # Project to road lane
        waypoint = self.world.get_map().get_waypoint(
            spawn_point.location,
            project_to_road=True,
            lane_type=carla.LaneType.Driving
        )

        spawn_point = waypoint.transform

        ego = None

        # Retry spawn
        for _ in range(10):

            ego = self.world.try_spawn_actor(vehicle_bp, spawn_point)

            if ego is not None:
                break

            spawn_point = random.choice(spawn_points)

        if ego is None:
            raise RuntimeError("Failed to spawn ego vehicle")

        self.ego_vehicle = ego

        print("Ego vehicle spawned")

        return ego


    # ==================================================
    # SPAWN NPC VEHICLES
    # ==================================================
    def spawn_npc(self):

        spawn_points = self.world.get_map().get_spawn_points()

        vehicle_bps = self.blueprints.filter("vehicle.*")

        random.shuffle(spawn_points)

        count = 0

        for spawn in spawn_points:

            if count >= MAX_NPC:
                break

            bp = random.choice(vehicle_bps)

            npc = self.world.try_spawn_actor(bp, spawn)

            if npc:

                npc.set_autopilot(True, self.tm.get_port())

                # safer driving behaviour
                self.tm.ignore_lights_percentage(npc, 0)
                self.tm.auto_lane_change(npc, True)
                self.tm.distance_to_leading_vehicle(npc, 4)

                self.npc_vehicles.append(npc)

                count += 1

        print(f"Spawned {len(self.npc_vehicles)} NPC vehicles")