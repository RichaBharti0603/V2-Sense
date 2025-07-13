import random
from vehicle_node import VehicleNode

class WorldSimulator:
    def __init__(self, num_vehicles=4):
        self.vehicles = []
        self.init_vehicles(num_vehicles)

    def init_vehicles(self, n):
        for i in range(n):
            vid = chr(65 + i)  # Vehicle IDs: A, B, C, ...
            x = random.randint(-100, 100)
            y = random.randint(-100, 100)
            speed = random.uniform(5, 20)  # m/s
            angle = random.randint(0, 360)
            node = VehicleNode(vid, x, y, speed, angle)
            self.vehicles.append(node)

    def step(self):
        for v in self.vehicles:
            v.update_position()

    def simulate(self):
        messages = []
        warnings = []
        self.step()
        for v in self.vehicles:
            messages.append(v.get_broadcast_message())
        for i in range(len(self.vehicles)):
            for j in range(i + 1, len(self.vehicles)):
                ttc = self.vehicles[i].check_ttc_with(self.vehicles[j])
                if ttc < float('inf'):
                    warnings.append(f"⚠️ Collision Risk: {self.vehicles[i].id} & {self.vehicles[j].id} in {ttc} sec")
        return messages, warnings
