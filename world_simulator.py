import random
import math

class Vehicle:
    def __init__(self, vid, x, y, angle, speed):
        self.id = vid
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.trail = [(x, y)]

    def move(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)

    def broadcast(self):
        return {
            "id": self.id,
            "position": [self.x, self.y],
            "angle": self.angle,
            "speed": self.speed
        }


class WorldSimulator:
    def __init__(self, num_vehicles=4, speed_min=5, speed_max=15):
        self.num_vehicles = num_vehicles
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.vehicles = self._generate_vehicles()

    def _generate_vehicles(self):
        vehicles = []
        for i in range(self.num_vehicles):
            x = random.randint(-100, 100)
            y = random.randint(-100, 100)
            angle = random.randint(0, 360)
            speed = random.uniform(self.speed_min, self.speed_max)
            vehicles.append(Vehicle(f"V{i+1}", x, y, angle, speed))
        return vehicles

    def simulate(self, do_move=True):
        if do_move:
            for v in self.vehicles:
                v.move()

        messages = [v.broadcast() for v in self.vehicles]
        warnings = self.detect_collisions()
        comm_links = self.generate_communication_links()
        return messages, warnings, comm_links

    def detect_collisions(self, threshold=15):
        warnings = []
        for i in range(len(self.vehicles)):
            for j in range(i + 1, len(self.vehicles)):
                v1 = self.vehicles[i]
                v2 = self.vehicles[j]
                dist = math.hypot(v1.x - v2.x, v1.y - v2.y)
                if dist < threshold:
                    warnings.append(f"{v1.id} may collide with {v2.id} (Distance: {dist:.2f})")
        return warnings

    def generate_communication_links(self, comm_radius=60):
        links = []
        for i in range(len(self.vehicles)):
            for j in range(i + 1, len(self.vehicles)):
                v1 = self.vehicles[i]
                v2 = self.vehicles[j]
                dist = math.hypot(v1.x - v2.x, v1.y - v2.y)
                if dist <= comm_radius:
                    links.append((v1.id, v2.id))
        return links
