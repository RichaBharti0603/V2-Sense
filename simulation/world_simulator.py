import random
from vehicle_node import VehicleNode

class WorldSimulator:
    def __init__(self, num_vehicles=4):
        self.vehicles = []
        self.time = 0
        self.init_vehicles(num_vehicles)

    def init_vehicles(self, n):
        for i in range(n):
            vid = chr(65 + i)  # 'A', 'B', ...
            x = random.randint(-100, 100)
            y = random.randint(-100, 100)
            speed = random.uniform(5, 20)  # m/s
            angle = random.randint(0, 360)  # direction in degrees
            node = VehicleNode(vid, x, y, speed, angle)
            self.vehicles.append(node)

    def update(self):
        for v in self.vehicles:
            v.update_position()

    def simulate_step(self):
        print(f"\n⏱️ Time: {self.time}s")
        self.update()

        # Show broadcast messages
        for v in self.vehicles:
            print(f"📡 {v.id} Broadcast: {v.get_broadcast_message()}")

        # Check for possible collisions
        for i in range(len(self.vehicles)):
            for j in range(i + 1, len(self.vehicles)):
                ttc = self.vehicles[i].check_ttc_with(self.vehicles[j])
                if ttc < float('inf'):
                    print(f"⚠️ Collision Risk: {self.vehicles[i].id} & {self.vehicles[j].id} in {ttc} sec")

        self.time += 1

# Run a sample simulation
if __name__ == "__main__":
    sim = WorldSimulator()
    for _ in range(5):  # Simulate 5 seconds
        sim.simulate_step()
