import math
import random

class Vehicle:
    def __init__(self, vid, x, y, speed, angle):
        self.id = vid
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle

    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

    def get_broadcast(self):
        return {
            "ID": self.id,
            "X": round(self.x, 2),
            "Y": round(self.y, 2),
            "SPEED": round(self.speed, 2),
            "ANGLE": round(self.angle, 2)
        }

class WorldSimulator:
    def __init__(self, num_vehicles=4, speed_min=5, speed_max=15):
        self.num_vehicles = num_vehicles
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.vehicles = self.generate_vehicles()

    def generate_vehicles(self):
        vehicles = []
        for i in range(self.num_vehicles):
            x = random.uniform(-80, 80)
            y = random.uniform(-80, 80)
            speed = random.uniform(self.speed_min, self.speed_max)
            angle = random.uniform(0, 360)
            vehicles.append(Vehicle(f"{chr(65+i)}", x, y, speed, angle))
        return vehicles

    def simulate(self, do_move=True):
        messages = []
        warnings = []

        if do_move:
            for v in self.vehicles:
                v.move()

        for v in self.vehicles:
            messages.append(v.get_broadcast())

        for i in range(len(self.vehicles)):
            for j in range(i + 1, len(self.vehicles)):
                v1 = self.vehicles[i]
                v2 = self.vehicles[j]
                ttc = self.time_to_collision(v1, v2)
                if ttc and ttc < 5:
                    warnings.append(f"⚠️ Vehicles {v1.id} and {v2.id} may collide in {round(ttc, 2)}s")

        return messages, warnings

    def time_to_collision(self, v1, v2):
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        dvx = v2.speed * math.cos(math.radians(v2.angle)) - v1.speed * math.cos(math.radians(v1.angle))
        dvy = v2.speed * math.sin(math.radians(v2.angle)) - v1.speed * math.sin(math.radians(v1.angle))

        dv_dot_d = dvx * dx + dvy * dy
        if dv_dot_d >= 0:
            return None

        dv2 = dvx**2 + dvy**2
        if dv2 == 0:
            return None

        t = -(dv_dot_d) / dv2
        if t < 0:
            return None

        closest_x = v1.x + v1.speed * math.cos(math.radians(v1.angle)) * t
        closest_y = v1.y + v1.speed * math.sin(math.radians(v1.angle)) * t
        closest_v2_x = v2.x + v2.speed * math.cos(math.radians(v2.angle)) * t
        closest_v2_y = v2.y + v2.speed * math.sin(math.radians(v2.angle)) * t

        distance = math.sqrt((closest_x - closest_v2_x)**2 + (closest_y - closest_v2_y)**2)
        if distance < 10:
            return t
        return None
