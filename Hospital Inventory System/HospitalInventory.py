import tkinter as tk
from tkinter import ttk, messagebox
import random
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Probability tables
rooms_occupied_table = [
    (1, 0.10, "01-10"),
    (2, 0.25, "11-25"),
    (3, 0.60, "26-60"),
    (4, 0.80, "61-80"),
    (5, 1.00, "81-100"),
]

lead_time_table = [
    (1, 0.40, "01-40"),
    (2, 0.75, "41-75"),
    (3, 1.00, "76-100"),
]


# Helper function
def get_random_value(randInt, table):
    rnd = randInt / 100
    for value, prob, _ in table:
        if rnd <= prob:
            return value


def theoretical_averages(table):
    return sum(value * (prob if i == 0 else prob - table[i - 1][1])
               for i, (value, prob, _) in enumerate(table))


def runSim(days=20, max_basement_inventory=30, review_period=6):
    max_ff_inventory = 10
    ff_inventory = 4
    basement_inventory = max_basement_inventory
    shortageFF = 0
    days_until_review = review_period - 1
    days_until_order_arrival = "-"
    basementShortage = 0
    total_demand = 0
    total_shortage_days = 0
    total_basement_shortage = 0
    lead_times = []
    daily_demand = []

    columns = ["Day", "NumOfRooms Rand", "Rooms Occupied (Boxes Demand)",
               "Beginning FF Inventory", "Shortage", "Ending FF Inventory",
               "Basement Inventory", "Basement Shortage", "Days Until Review",
               "Days Until Order Arrival"]

    simulation_data = []

    for day in range(1, days + 1):
        shortageFF = 0
        beginningInv = ff_inventory
        rooms_rand = random.randint(1, 100)
        demand = get_random_value(rooms_rand, rooms_occupied_table)
        total_demand += demand
        daily_demand.append(demand)

        if ff_inventory >= demand:
            ff_inventory -= demand
            if ff_inventory == 0:
                ff_inventory += min(10, basement_inventory)
                basement_inventory -= min(10, basement_inventory)
        else:
            shortageFF = demand - ff_inventory
            total_shortage_days += 1
            if basement_inventory > 0:
                ff_inventory += min(10, basement_inventory)
                basement_inventory -= min(10, basement_inventory)
                if demand > ff_inventory:
                    basementShortage += demand - ff_inventory
                ff_inventory = max(0, ff_inventory - demand)
            elif basement_inventory == 0:
                basementShortage += demand - ff_inventory
                total_basement_shortage += 1
                ff_inventory = 0

        if days_until_review == 0:
            lead_time_rand = random.randint(1, 100)
            lead_time = get_random_value(lead_time_rand, lead_time_table)
            lead_times.append(lead_time)
            days_until_order_arrival = lead_time
        else:
            lead_time_rand = "-"

        endingInv = ff_inventory

        simulation_data.append([
            day, rooms_rand, demand, beginningInv, shortageFF, endingInv,
            basement_inventory, basementShortage, days_until_review, days_until_order_arrival
        ])

        if days_until_review > 0:
            days_until_review -= 1
        else:
            days_until_review = review_period - 1

        if isinstance(days_until_order_arrival, int):
            days_until_order_arrival -= 1
            if days_until_order_arrival == 0:
                basement_inventory = max_basement_inventory
                temp_basement = basement_inventory
                basement_inventory = max(0, basement_inventory - basementShortage)
                basementShortage = max(0, basementShortage - temp_basement)
                days_until_order_arrival = "-"

    simulation_df = pd.DataFrame(simulation_data, columns=columns)

    avgFF = sum(row[5] for row in simulation_data) // len(simulation_data)
    avgBasement = sum(row[6] for row in simulation_data) // len(simulation_data)
    experimental_avg_demand = total_demand / days
    experimental_avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0
    theoretical_avg_demand = theoretical_averages(rooms_occupied_table)
    theoretical_avg_lead_time = theoretical_averages(lead_time_table)

    return simulation_df, {
        "avg_ff": avgFF,
        "avg_basement": avgBasement,
        "total_shortage_days": total_shortage_days,
        "total_basement_shortage": total_basement_shortage,
        "experimental_avg_demand": experimental_avg_demand,
        "experimental_avg_lead_time": experimental_avg_lead_time,
        "theoretical_avg_demand": theoretical_avg_demand,
        "theoretical_avg_lead_time": theoretical_avg_lead_time,
        "basement_shortage": basementShortage
    }


def optimalMaxBasement():
    for max_basement in range(10, 40,5):
        _, stats = runSim(40, max_basement, 6)
        if stats["basement_shortage"] == 0:
            return max_basement


def find_best_value(func):
    results = [func() for _ in range(200)]
    return Counter(results).most_common(1)[0][0]


def optimalReviewPeriod():
    for reviewPeriod in range(5, 15):
        _, stats = runSim(20, 30, reviewPeriod)
        if stats["basement_shortage"] != 0:
            return reviewPeriod - 1


def find_optimal_combination():
    optimal_combination = None
    min_basement_shortage = float('inf')
    for max_basement in range(20, 40,2):
        for review_period in range(2, 11):
            _, stats = runSim(days=100, max_basement_inventory=max_basement, review_period=review_period)
            if stats["basement_shortage"] < min_basement_shortage:
                min_basement_shortage = stats["basement_shortage"]
                optimal_combination = (max_basement, review_period)
            if stats["basement_shortage"] == 0:
                return optimal_combination
    return optimal_combination


class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Simulation")
        self.create_input_section()
        self.create_results_section()
        self.root.minsize(1300, 600)

    def create_input_section(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10, padx=10, fill="x")

        tk.Label(frame, text="Days").grid(row=0, column=0, padx=5, pady=5)
        self.days_entry = ttk.Entry(frame)
        self.days_entry.grid(row=0, column=1, padx=5, pady=5)
        self.days_entry.insert(0, "20")

        tk.Label(frame, text="Max Basement Inventory").grid(row=1, column=0, padx=5, pady=5)
        self.basement_entry = ttk.Entry(frame)
        self.basement_entry.grid(row=1, column=1, padx=5, pady=5)
        self.basement_entry.insert(0, "30")

        tk.Label(frame, text="Review Period").grid(row=2, column=0, padx=5, pady=5)
        self.review_entry = ttk.Entry(frame)
        self.review_entry.grid(row=2, column=1, padx=5, pady=5)
        self.review_entry.insert(0, "6")

        tk.Label(frame, text="Number of Runs").grid(row=3, column=0, padx=5, pady=5)
        self.runs_entry = ttk.Entry(frame)
        self.runs_entry.grid(row=3, column=1, padx=5, pady=5)
        self.runs_entry.insert(0, "10")

        self.run_single_btn = ttk.Button(frame, text="Run Single Simulation", command=self.run_single_simulation)
        self.run_single_btn.grid(row=4, column=0, padx=5, pady=5)

        self.run_multiple_btn = ttk.Button(frame, text="Run Multiple Simulations",
                                           command=self.run_multiple_simulations)
        self.run_multiple_btn.grid(row=4, column=1, padx=5, pady=5)

        self.plot_histograms_btn = ttk.Button(frame, text="Display Histograms", command=self.plot_histograms)
        self.plot_histograms_btn.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    def create_results_section(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas = canvas
        self.scrollable_frame = scrollable_frame
        self.results_frame = ttk.Frame(scrollable_frame)
        self.results_frame.pack(fill="both", expand=True)

    def display_results(self, result=None, stats=None):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Display table if result is provided
        if result is not None and isinstance(result, pd.DataFrame):
            for i, column in enumerate(result.columns):
                label = tk.Label(self.results_frame, text=column, relief="solid", padx=5, pady=5, bg="lightgray")
                label.grid(row=0, column=i, sticky="nsew")
            for row_index, row in result.iterrows():
                for col_index, value in enumerate(row):
                    label = tk.Label(self.results_frame, text=value, relief="solid", padx=5, pady=5)
                    label.grid(row=row_index + 1, column=col_index, sticky="nsew")

            next_row = len(result) + 1  # Place stats below the table
            num_columns = len(result.columns)
        else:
            # If no table, set the starting row and column count
            next_row = 0
            num_columns = 1

        # Display stats in a styled frame
        if stats:
            stats_frame = ttk.LabelFrame(self.results_frame, text="Simulation Statistics", padding=(10, 5))
            stats_frame.grid(row=next_row, column=0, columnspan=num_columns, pady=10, sticky="ew")

            # Add stats as labels in the frame
            for i, line in enumerate(stats.split("\n")):
                if line.strip():  # Skip empty lines
                    label = tk.Label(stats_frame, text=line, anchor="w", padx=5, pady=2)
                    label.grid(row=i, column=0, sticky="w")
        self.canvas.yview_moveto(0)


    def run_single_simulation(self):
        try:
            days = int(self.days_entry.get())
            max_basement = int(self.basement_entry.get())
            review_period = int(self.review_entry.get())
            simulation_df, stats = runSim(days, max_basement, review_period)

            optimal_max_basement = find_best_value(optimalMaxBasement)
            optimal_review_period = find_best_value(optimalReviewPeriod)
            optimal_combination = find_best_value(find_optimal_combination)

            stats_str = (
                f"Average FF Inventory: {stats['avg_ff']}\n"
                f"Average Basement Inventory: {stats['avg_basement']}\n"
                f"Total Shortage Days: {stats['total_shortage_days']}\n"
                f"Total Basement Shortage: {stats['total_basement_shortage']}\n"
                f"Experimental Avg Demand: {stats['experimental_avg_demand']:.2f}\n"
                f"Experimental Avg Lead Time: {stats['experimental_avg_lead_time']:.2f}\n"
                f"Theoretical Avg Demand: {stats['theoretical_avg_demand']:.2f}\n"
                f"Theoretical Avg Lead Time: {stats['theoretical_avg_lead_time']:.2f}\n"
                f"Optimal Max Basement: {optimal_max_basement}\n"
                f"Optimal Review Period: {optimal_review_period}\n"
                f"Optimal Combination: {optimal_combination}\n"
            )

            self.display_results(simulation_df, stats_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")

    def run_multiple_simulations(self):
        try:
            runs = int(self.runs_entry.get())
            days = int(self.days_entry.get())
            max_basement = int(self.basement_entry.get())
            review_period = int(self.review_entry.get())

            averages = {
                "FF Inventory": 0,
                "Basement Inventory": 0,
                "Shortage Days": 0,
                "Demand": 0,
                "Lead Time": 0,
                "Basement Shortage": 0,
            }

            for _ in range(runs):
                _, stats = runSim(days, max_basement, review_period)
                averages["FF Inventory"] += stats["avg_ff"]
                averages["Basement Inventory"] += stats["avg_basement"]
                averages["Shortage Days"] += stats["total_shortage_days"]
                averages["Demand"] += stats["experimental_avg_demand"]
                averages["Lead Time"] += stats["experimental_avg_lead_time"]
                averages["Basement Shortage"] += stats["basement_shortage"]

            for key in averages.keys():
                averages[key] /= runs

            # Prepare a stats string
            stats_str = (
                f"Results for {runs} runs:\n"
                f"------------------------------\n"
                f"Average FF Inventory: {averages['FF Inventory']:.2f}\n"
                f"Average Basement Inventory: {averages['Basement Inventory']:.2f}\n"
                f"Average Shortage Days: {averages['Shortage Days']:.2f}\n"
                f"Average Demand: {averages['Demand']:.2f}\n"
                f"Average Lead Time: {averages['Lead Time']:.2f}\n"
                f"Average Basement Shortage: {averages['Basement Shortage']:.2f}\n"
            )

            # Call display_results with only stats
            self.display_results(None, stats_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")

    def plot_histograms(self):
        try:
            days = int(self.days_entry.get())
            max_basement = int(self.basement_entry.get())
            review_period = int(self.review_entry.get())

            # Run simulation
            simulation_df, _ = runSim(days, max_basement, review_period)

            # Extract daily demand and shortages from the DataFrame
            daily_demand = simulation_df["Rooms Occupied (Boxes Demand)"]
            daily_shortage = simulation_df["Shortage"]

            # Create a new window for displaying the histograms
            hist_window = tk.Toplevel(self.root)
            hist_window.title("Histograms")

            # Create a Matplotlib figure
            fig = Figure(figsize=(8, 6))
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            # Plot Demand Histogram
            ax1.hist(daily_demand, bins=range(1, max(daily_demand) + 2), edgecolor='black', color='skyblue')
            ax1.set_title("Daily Demand")
            ax1.set_xlabel("Demand")
            ax1.set_ylabel("Frequency")

            # Plot Shortage Histogram
            ax2.hist(daily_shortage, bins=range(0, max(daily_shortage) + 2), edgecolor='black', color='salmon')
            ax2.set_title("Daily Shortages")
            ax2.set_xlabel("Shortages")
            ax2.set_ylabel("Frequency")

            # Embed the figure in the Tkinter window
            canvas = FigureCanvasTkAgg(fig, master=hist_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")


root = tk.Tk()
app = SimulationApp(root)
root.mainloop()