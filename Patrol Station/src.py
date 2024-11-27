import tkinter as tk
from tkinter import ttk
import random

class PetrolStationSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Petrol Station Simulation")

        self.canvas = tk.Canvas(root, width=800, height=600, bg="lightblue")
        self.canvas.pack()

        # Create pumps (90 Octane, 95 Octane, Gas)
        self.pumps = {
            "90 Octane": {"coords": (100, 100), "queue": [], "color": "yellow"},
            "95 Octane": {"coords": (400, 100), "queue": [], "color": "green"},
            "Gas": {"coords": (700, 100), "queue": [], "color": "orange"},
        }
        self.create_pumps()

        # Simulation parameters
        self.cars = []
        self.car_count = 0
        self.running = False
        self.car_icons = []
        self.current_time = 0  # Simulation clock

        # Add control buttons
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.start_button = tk.Button(self.control_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_simulation)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.grid(row=0, column=2, padx=5)

    def create_pumps(self):
        """Draw pumps on the canvas."""
        for pump_name, pump_data in self.pumps.items():
            x, y = pump_data["coords"]
            self.canvas.create_rectangle(x - 30, y - 30, x + 30, y + 30, fill=pump_data["color"], tags=pump_name)
            self.canvas.create_text(x, y + 50, text=pump_name, font=("Arial", 12))

    def generate_car(self):
        """Generate a car and assign it to a pump."""
        self.car_count += 1
        car_id = self.car_count  # Assign a number to the car
        category = random.choice(["A", "B", "C"])

        # Assign to a pump based on category
        if category == "A":
            pump = "95 Octane"
        elif category == "B":
            pump = "90 Octane" if len(self.pumps["90 Octane"]["queue"]) <= 3 else "95 Octane"
        else:  # Category C
            pump = "Gas" if random.random() < 0.6 else "90 Octane"

        car = {
            "id": car_id,
            "category": category,
            "pump": pump,
            "state": "waiting",
        }
        self.cars.append(car)
        self.pumps[pump]["queue"].append(car)

        # Add car to canvas with number
        x, y = 50, 500  # Starting position
        car_rect = self.canvas.create_rectangle(x, y, x + 30, y + 20, fill="red", tags=f"car_{car_id}")
        car_number = self.canvas.create_text(x + 15, y + 10, text=str(car_id), font=("Arial", 10), tags=f"car_{car_id}")
        self.car_icons.append({"car": car, "rect": car_rect, "text": car_number, "x": x, "y": y})

    def move_cars(self):
        """Animate cars moving to their respective pumps and handle servicing."""
        for car_data in self.car_icons:
            car = car_data["car"]
            rect = car_data["rect"]
            text = car_data["text"]
            pump_coords = self.pumps[car["pump"]]["coords"]

            if car["state"] == "waiting":
                # Move to queue position
                x, y = car_data["x"], car_data["y"]
                target_x, target_y = pump_coords[0], pump_coords[1] + 50 + 20 * self.pumps[car["pump"]]["queue"].index(car)

                dx = target_x - x
                dy = target_y - y
                distance = (dx**2 + dy**2)**0.5

                if distance > 5:
                    move_x = dx / distance * 5
                    move_y = dy / distance * 5
                    self.canvas.move(rect, move_x, move_y)
                    self.canvas.move(text, move_x, move_y)  # Move the number along with the car
                    car_data["x"] += move_x
                    car_data["y"] += move_y
                else:
                    # Car has reached queue position
                    if self.pumps[car["pump"]]["queue"][0] == car:  # First in queue starts service
                        car["state"] = "servicing"

            elif car["state"] == "servicing":
                # Simulate servicing; for simplicity, cars leave immediately after reaching pump
                self.canvas.move(rect, 10, 0)  # Move car off canvas
                self.canvas.move(text, 10, 0)  # Move number off canvas
                car_data["x"] += 10
                if car_data["x"] > 800:
                    self.canvas.delete(rect)
                    self.canvas.delete(text)
                    self.car_icons.remove(car_data)

    def start_simulation(self):
        """Start the simulation."""
        self.running = True
        self.simulation_loop()

    def pause_simulation(self):
        """Pause the simulation."""
        self.running = False

    def reset_simulation(self):
        """Reset the simulation."""
        self.running = False
        self.car_count = 0
        self.cars = []
        for pump in self.pumps.values():
            pump["queue"] = []
        self.car_icons = []
        self.canvas.delete("all")
        self.create_pumps()

    def simulation_loop(self):
        """Main simulation loop."""
        if not self.running:
            return

        # Generate a new car every few frames
        if random.random() < 0.1:
            self.generate_car()

        # Move cars and handle servicing
        self.move_cars()

        # Continue simulation
        self.root.after(50, self.simulation_loop)


# Run the simulation
root = tk.Tk()
app = PetrolStationSimulation(root)
root.mainloop()
