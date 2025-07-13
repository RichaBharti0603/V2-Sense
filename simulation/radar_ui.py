import tkinter as tk
import math

# Create main window
root = tk.Tk()
root.title("V2Sense - Radar Collision Warning")
canvas_size = 400
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="black")
canvas.pack()

# Radar center (Your vehicle)
center_x, center_y = canvas_size // 2, canvas_size // 2
canvas.create_oval(center_x-5, center_y-5, center_x+5, center_y+5, fill="blue", outline="white")
canvas.create_text(center_x, center_y + 15, fill="white", text="YOU")

# Example nearby vehicles (relative positions)
vehicles = [
    {"id": "A", "x": 50, "y": -80, "vx": -2, "vy": 1},
    {"id": "B", "x": -100, "y": 60, "vx": 2, "vy": -1},
    {"id": "C", "x": 120, "y": 100, "vx": -1, "vy": -1}
]

# Update function for animation
def update():
    canvas.delete("vehicle")

    for v in vehicles:
        # Update positions
        v["x"] += v["vx"]
        v["y"] += v["vy"]

        # Convert to canvas coordinates
        cx = center_x + v["x"]
        cy = center_y + v["y"]

        # Distance to "you"
        dist = math.sqrt(v["x"]**2 + v["y"]**2)

        # Red = collision warning, Green = safe
        color = "red" if dist < 50 else "green"
        canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=color, tags="vehicle")
        canvas.create_line(cx, cy, cx - v["vx"]*5, cy - v["vy"]*5, fill="white", arrow=tk.LAST, tags="vehicle")
        canvas.create_text(cx + 10, cy, fill="white", text=f"{v['id']}", tags="vehicle")

    root.after(100, update)

# Start animation loop
update()
root.mainloop()
