import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt

# Set Pandas display options to show all columns and rows without truncation
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.width', None)  # Do not truncate columns by width
pd.set_option('display.max_colwidth', None)  # Show the full content of each column

# Function to generate car category based on probabilities
def generate_car_category():
    rand = random.random()
    if rand <= 0.2:
        return "A"
    elif rand <= 0.55:
        return "B"
    else:
        return "C"

# Function for service time based on car category
def service_time(category):
    rand = random.random()
    if category in ["A", "B"]:  # Table 2
        if rand <= 0.2:
            return 1
        elif rand <= 0.5:
            return 2
        else:
            return 3
    elif category == "C":  # Table 3
        if rand <= 0.2:
            return 3
        elif rand <= 0.7:
            return 5
        else:
            return 7

# Function for inter-arrival time
def inter_arrival_time():
    rand = random.random()
    if rand <= 0.17:
        return 0
    elif rand <= 0.4:
        return 1
    elif rand <= 0.65:
        return 2
    else:
        return 3

# Constants
n_cars = 10000
pump_queues = {"95": [], "90": [], "Gas": []}
pump_idle_times = {"95": 0, "90": 0, "Gas": 0}
max_queue_length = {"95": 0, "90": 0, "Gas": 0}

# Simulation data
categories = [generate_car_category() for _ in range(n_cars)]
inter_arrival_times = [inter_arrival_time() for _ in range(n_cars)]
arrival_times = np.cumsum(inter_arrival_times)
service_times = [service_time(cat) for cat in categories]

# Data for each car
service_begins = []
service_ends = []
waiting_times = []
pumps = []

# Simulation loop
for i in range(n_cars):
    category = categories[i]
    arrival = arrival_times[i]

    if category == "A":
        selected_pump = "95"
    elif category == "B":
        # Category B decides based on queue length and probability
        if len(pump_queues["90"]) > 3 and random.random() <= 0.6:
            selected_pump = "95"
        else:
            selected_pump = "90"
    else:  # Category C
        # Category C decides based on queue length and probability
        if len(pump_queues["Gas"]) > 4 and random.random() <= 0.4:
            selected_pump = "90"
        else:
            selected_pump = "Gas"

    pump_queue = pump_queues[selected_pump]
    start_time = max(arrival, pump_queue[-1][1] if pump_queue else 0)
    end_time = start_time + service_times[i]
    waiting_time = max(0, start_time - arrival)

    service_begins.append(start_time)
    service_ends.append(end_time)
    waiting_times.append(waiting_time)
    pumps.append(selected_pump)

    # Update pump queue and stats
    pump_queue.append((start_time, end_time))
    max_queue_length[selected_pump] = max(max_queue_length[selected_pump], len(pump_queue))

    # Idle time calculation
    if len(pump_queue) == 1:  # First car at the pump
        pump_idle_times[selected_pump] += start_time - (arrival_times[i - 1] if i > 0 else 0)

# Results
data = pd.DataFrame({
    "Car": range(1, n_cars + 1),
    "Category": categories,
    "Arrival Time": arrival_times,
    "Service Time": service_times,
    "Service Begins": service_begins,
    "Service Ends": service_ends,
    "Waiting Time": waiting_times,
    "Pump": pumps
})
# Measure Calculations
# Average service time for each category
avg_service_time = {}
for category in ["A", "B", "C"]:
    avg_service_time[category] = round(data[data["Category"] == category]["Service Time"].mean(), 2)

# Average waiting time for each pump
avg_waiting_time_per_pump = {}
for pump in ["95", "90", "Gas"]:
    avg_waiting_time_per_pump[pump] = round(data[data["Pump"] == pump]["Waiting Time"].mean(), 2)

# Overall average waiting time
overall_avg_waiting_time = round(data["Waiting Time"].mean(), 2)

# Idle time ratios
idle_time_ratios = {}
for pump in pump_idle_times:
    idle_time_ratios[pump] = round(pump_idle_times[pump] / service_ends[-1], 2)

# Maximum queue lengths (already stored)
max_queue_lengths = max_queue_length

# Waiting probabilities
waiting_probabilities = {}
for pump in pump_queues:
    waiting_probabilities[pump] = round(len(data[data["Pump"] == pump]) / n_cars, 2)

# Theoretical values
th_avg_service = {}
th_avg_service["A"] = round(1 * 0.2 + 2 * 0.3 + 3 * 0.5, 2)
th_avg_service["B"] = round(1 * 0.2 + 2 * 0.3 + 3 * 0.5, 2)
th_avg_service["C"] = round(3 * 0.2 + 5 * 0.5 + 7 * 0.3, 2)
th_avg_inter_time = round(0 * 0.17 + 1 * 0.23 + 2 * 0.25 + 3 * 0.35, 2)

# Extra pump analysis
add_wait_times = {}
for pump in ["95", "90", "Gas"]:
    reduced_waiting_times = []
    for index, row in data.iterrows():
        if row["Pump"] == pump:
            reduced_waiting_times.append(max(0, row["Waiting Time"] - 1))  # Simulate reduction
        else:
            reduced_waiting_times.append(row["Waiting Time"])
    add_wait_times[pump] = round(sum(reduced_waiting_times) / len(reduced_waiting_times), 2)

# Results Display
print(data)
print("\nStatistics:")
print("1. Average Service Time per Category:")
for category, avg_time in avg_service_time.items():
    print(f"   {category}: {avg_time}")
print("\n2. Average Waiting Time per Pump:")
for pump, avg_time in avg_waiting_time_per_pump.items():
    print(f"   {pump}: {avg_time}")
print(f"   Overall Average Waiting Time: {overall_avg_waiting_time}")
print("\n3. Maximum Queue Lengths:")
for pump, length in max_queue_lengths.items():
    print(f"   {pump}: {length}")
print("\n4. Waiting Probabilities per Pump:")
for pump, prob in waiting_probabilities.items():
    print(f"   {pump}: {prob}")
print("\n5. Idle Time Ratios:")
for pump, ratio in idle_time_ratios.items():
    print(f"   {pump}: {ratio}")
print("\nPolicy Questions:")
print("6. Theoretical vs Experimental Average Service Time per Category:")
for category in avg_service_time:
    print(f"   Category {category}: Theoretical = {th_avg_service[category]}, Experimental = {avg_service_time[category]}")
print("7. Theoretical vs Experimental Average Inter-Arrival Time:")
exp_avg_inter_time = round(sum(inter_arrival_times) / len(inter_arrival_times), 2)
print(f"   Theoretical = {th_avg_inter_time}, Experimental = {exp_avg_inter_time}")
print("8. Effect of Adding Extra Pump:")
for pump, avg_time in add_wait_times.items():
    print(f"   Adding an extra {pump} pump reduces average waiting time to {avg_time}")
for pump in ["95", "90", "Gas"]:
    # Filter data for the current pump
    pump_data = data[data["Pump"] == pump]
# Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

# Service Time Histogram
    ax1.hist(pump_data["Service Time"], bins=10, color='skyblue', edgecolor='blue')
    ax1.set_title(f"Service Time Histogram for {pump} Pump")
    ax1.set_xlabel("Service Time (minutes)")
    ax1.set_ylabel("Frequency")
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Waiting Time Histogram
    ax2.hist(pump_data["Waiting Time"], bins=10, color='lightcoral', edgecolor='red')
    ax2.set_title(f"Waiting Time Histogram for {pump} Pump")
    ax2.set_xlabel("Waiting Time (minutes)")
    ax2.set_ylabel("Frequency")
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()
