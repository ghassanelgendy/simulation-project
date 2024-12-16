import tkinter as tk
from tkinter import ttk, messagebox
import random
import pandas as pd
from collections import Counter

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
    for max_basement in range(10, 40):
        _, stats = runSim(20, max_basement, 6)
        if stats["basement_shortage"] == 0:
            return max_basement


def find_best_value(func):
    results = [func() for _ in range(500)]
    return Counter(results).most_common(1)[0][0]


def optimalReviewPeriod():
    for reviewPeriod in range(5, 12):
        _, stats = runSim(20, 30, reviewPeriod)
        if stats["basement_shortage"] != 0:
            return reviewPeriod - 1


def find_optimal_combination():
    optimal_combination = None
    min_basement_shortage = float('inf')
    for max_basement in range(10, 40):
        for review_period in range(5, 12):
            _, stats = runSim(days=20, max_basement_inventory=max_basement, review_period=review_period)
            if stats["basement_shortage"] < min_basement_shortage:
                min_basement_shortage = stats["basement_shortage"]
                optimal_combination = (max_basement, review_period)
            if stats["basement_shortage"] == 0:
                return optimal_combination
    return optimal_combination


class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation GUI")
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

    def display_results(self, result, stats=None):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if isinstance(result, pd.DataFrame):
            for i, column in enumerate(result.columns):
                label = tk.Label(self.results_frame, text=column, relief="solid", padx=5, pady=5)
                label.grid(row=0, column=i, sticky="nsew")
            for row_index, row in result.iterrows():
                for col_index, value in enumerate(row):
                    label = tk.Label(self.results_frame, text=value, relief="solid", padx=5, pady=5)
                    label.grid(row=row_index + 1, column=col_index, sticky="nsew")
        elif isinstance(result, str):
            label = tk.Label(self.results_frame, text=result, font=("Arial", 16), padx=5, pady=5)
            label.grid(row=0, column=0, sticky="nsew")

        if stats:
            label = tk.Label(self.results_frame, text=stats, font=("Arial", 12), padx=5, pady=5, justify="left")
            label.grid(row=len(self.results_frame.winfo_children()) + 1, column=0, sticky="w", padx=5, pady=5)

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
                f"Simulation Statistics:\n"
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
                "ff_inventory": 0,
                "basement_inventory": 0,
                "shortage_days": 0,
                "avg_demand": 0,
                "avg_lead_time": 0,
                "basement_shortage": 0,
            }

            for _ in range(runs):
                _, stats = runSim(days, max_basement, review_period)
                averages["ff_inventory"] += stats["avg_ff"]
                averages["basement_inventory"] += stats["avg_basement"]
                averages["shortage_days"] += stats["total_shortage_days"]
                averages["avg_demand"] += stats["experimental_avg_demand"]
                averages["avg_lead_time"] += stats["experimental_avg_lead_time"]
                averages["basement_shortage"] += stats["basement_shortage"]

            for key in averages.keys():
                averages[key] /= runs

            stats_str = (
                f"Simulation Results after {runs} runs:\n"
                f"Avg FF Inventory: {averages['ff_inventory']:.2f}\n"
                f"Avg Basement Inventory: {averages['basement_inventory']:.2f}\n"
                f"Avg Shortage Days: {averages['shortage_days']:.2f}\n"
                f"Avg Demand: {averages['avg_demand']:.2f}\n"
                f"Avg Lead Time: {averages['avg_lead_time']:.2f}\n"
                f"Total Basement Shortage: {averages['basement_shortage']:.2f}\n"
            )

            self.display_results(stats_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")



root = tk.Tk()
app = SimulationApp(root)
root.mainloop()