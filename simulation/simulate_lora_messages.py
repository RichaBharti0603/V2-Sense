import random
import time

# Generate a random compass direction
def random_direction():
    return random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

# Generate message for a simulated vehicle
def generate_vehicle_message(vehicle_id):
    lat = round(28.6000 + random.uniform(-0.1, 0.1), 4)
    lon = round(77.2000 + random.uniform(-0.1, 0.1), 4)
    speed = random.randint(10, 60)  # km/h
    direction = random_direction()
    return f"ID:{vehicle_id},LAT:{lat},LON:{lon},SPEED:{speed},DIR:{direction}"

# Simulate broadcast every second
def simulate_broadcast():
    vehicle_ids = [1, 2, 3, 4]
    for _ in range(5):  # simulate 5 rounds
        print("----- LoRa Broadcast Round -----")
        for vid in vehicle_ids:
            print(generate_vehicle_message(vid))
        time.sleep(1)

# Run simulation
simulate_broadcast()
