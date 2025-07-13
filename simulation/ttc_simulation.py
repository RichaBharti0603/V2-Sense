import math

# Function to calculate distance between two 2D points (x, y)
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to calculate relative velocity
def calculate_relative_velocity(v1, v2):
    return abs(v1 - v2)

# Time to Collision Calculation
def time_to_collision(pos1, speed1, pos2, speed2):
    distance = calculate_distance(pos1[0], pos1[1], pos2[0], pos2[1])
    rel_speed = calculate_relative_velocity(speed1, speed2)

    if rel_speed == 0:
        return float('inf')  # No closing speed = no collision

    ttc = distance / rel_speed
    return round(ttc, 2)

# Example 1: Vehicle A at (0,0) going 15 m/s, B at (45,0) going 5 m/s
vehicle_A = {"pos": (0, 0), "speed": 15}
vehicle_B = {"pos": (45, 0), "speed": 5}

ttc_result = time_to_collision(vehicle_A["pos"], vehicle_A["speed"],
                               vehicle_B["pos"], vehicle_B["speed"])

print(f"Time to Collision: {ttc_result} seconds")
