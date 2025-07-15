import random
import math

class Vehicle:
    def __init__(self, id, x, y, angle, speed):
        self.id = id
        self.x = x
        self.y = y
        self.angle = angle  # in degrees
        self.speed = speed
        self.trail = [(x, y)]

    def move(self):
        rad = math.radians(self.angle)
        dx = self.speed * math.cos(rad)
        dy = self.speed * math.sin(rad)
        self.x += dx
        self.y += dy
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class WorldSimulator:
    def __init__(self, num_vehicles=4, speed_min=5, speed_max=15):
        self.num_vehicles = num_vehicles
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.vehicles = self._spawn_vehicles()

    def _spawn_vehicles(self):
        vehicles = []
        for i in range(self.num_vehicles):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            angle = random.uniform(0, 360)
            speed = random.uniform(self.speed_min, self.speed_max)
            vehicles.append(Vehicle(id=i, x=x, y=y, angle=angle, speed=speed))
        return vehicles

    def simulate(self, do_move=True):
        messages = []
        warnings = []
        comm_links = []

        if do_move:
            for v in self.vehicles:
                v.move()

        # Broadcasting vehicle positions
        for v in self.vehicles:
            messages.append({
                "vehicle_id": v.id,
                "x": round(v.x, 2),
                "y": round(v.y, 2),
                "angle": round(v.angle, 2),
                "speed": round(v.speed, 2)
            })

        # Collision prediction & communication
        for i in range(len(self.vehicles)):
            for j in range(i + 1, len(self.vehicles)):
                v1 = self.vehicles[i]
                v2 = self.vehicles[j]
                dist = v1.distance_to(v2)

                # Check communication distance (< 40m)
                if dist < 40:
                    comm_links.append((v1.id, v2.id))

                # Simple collision warning if distance < threshold
                if dist < 15:
                    warning_msg = f"Vehicles {v1.id} and {v2.id} are too close! Distance: {round(dist, 1)}m"
                    warnings.append(warning_msg)

        return messages, warnings, comm_links
