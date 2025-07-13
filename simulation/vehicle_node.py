import math
import random

class VehicleNode:
    def __init__(self, vehicle_id, x, y, speed, angle_deg):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.speed = speed  # m/s
        self.angle_deg = angle_deg
        self.vx = speed * math.cos(math.radians(angle_deg))
        self.vy = speed * math.sin(math.radians(angle_deg))

    def update_position(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def get_broadcast_message(self):
        return {
            "ID": self.id,
            "X": round(self.x, 2),
            "Y": round(self.y, 2),
            "SPEED": self.speed,
            "ANGLE": self.angle_deg
        }

    def check_ttc_with(self, other, collision_distance=5, time_step=0.1, max_time=10):
        for t in range(int(max_time / time_step)):
            dt = t * time_step
            fx1, fy1 = self.x + self.vx * dt, self.y + self.vy * dt
            fx2, fy2 = other.x + other.vx * dt, other.y + other.vy * dt
            dist = math.hypot(fx1 - fx2, fy1 - fy2)
            if dist <= collision_distance:
                return round(dt, 2)
        return float('inf')

# Test Example
if __name__ == "__main__":
    a = VehicleNode("A", 0, 0, 15, 0)     # Moves right
    b = VehicleNode("B", 100, 10, 10, 180)  # Moves left

    print("Vehicle A:", a.get_broadcast_message())
    print("Vehicle B:", b.get_broadcast_message())

    ttc = a.check_ttc_with(b)
    print(f"Predicted Time to Collision: {ttc} seconds" if ttc != float('inf') else "No collision predicted.")
