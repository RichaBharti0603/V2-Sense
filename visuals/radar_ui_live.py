import tkinter as tk
import math
from vehicle_node import VehicleNode
from world_simulator import WorldSimulator

class RadarVisualizer:
    def __init__(self, root, simulator):
        self.sim = simulator
        self.canvas_size = 600
        self.center = self.canvas_size // 2
        self.root = root
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='black')
        self.canvas.pack()
        self.vehicle_colors = {}

        self.refresh()

    def draw_vehicle(self, vehicle):
        scale = 2  # adjust to zoom in/out
        x = self.center + vehicle.x * scale
        y = self.center - vehicle.y * scale

        color = self.vehicle_colors.get(vehicle.id, self.random_color())
        self.vehicle_colors[vehicle.id] = color

        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color)
        self.canvas.create_text(x + 10, y, text=vehicle.id, fill='white', font=('Arial', 8))

    def random_color(self):
        import random
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def draw_radar_circle(self):
        self.canvas.create_oval(50, 50, self.canvas_size - 50, self.canvas_size - 50, outline='green')

    def refresh(self):
        self.canvas.delete("all")
        self.draw_radar_circle()
        self.sim.simulate_step()
        for vehicle in self.sim.vehicles:
            self.draw_vehicle(vehicle)

        self.root.after(1000, self.refresh)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("V2Sense Radar UI")
    sim = WorldSimulator(num_vehicles=4)
    app = RadarVisualizer(root, sim)
    root.mainloop()
