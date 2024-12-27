import tkinter as tk
from builtins import *
from tkinter import ttk, scrolledtext
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import os

# to display everything in the dataframe
pd.set_option('display.max_columns', None)  
pd.set_option('display.max_rows', None)  
pd.set_option('display.width', None)  # don't wrap the lines
pd.set_option('display.max_colwidth', None)  # Show tfull colun

# uses given probabilites to generate a category
def generate_car_category():
    rand = random.random()
    if rand <= 0.2:
        return "A"
    elif rand <= 0.55:
        return "B"
    else:
        return "C"

#  service time based on car category
def service_time(category):
    rand = random.random()
    if category in ["A", "B"]: 
        if rand <= 0.2:
            return 1
        elif rand <= 0.5:
            return 2
        else:
            return 3
    elif category == "C": 
        if rand <= 0.2:
            return 3
        elif rand <= 0.7:
            return 5
        else:
            return 7

#inter-arrival time
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


def run_simulation():
    global data
    current_queue_length = {"95": 0, "90": 0, "Gas": 0}
    n_cars = int(num_cars_entry.get())
    pump_queues = {"95": [], "90": [], "Gas": []} # list to store the queue of each pump
    pump_idle_times = {"95": 0, "90": 0, "Gas": 0}
    last_end_time = {"95": 0, "90": 0, "Gas": 0}
    max_queue_length = {"95": 0, "90": 0, "Gas": 0}

    categories = [generate_car_category() for _ in range(n_cars)]
    inter_arrival_times = [inter_arrival_time() for _ in range(n_cars)]
    arrival_times = np.cumsum(inter_arrival_times)
    service_times = [service_time(cat) for cat in categories]

    service_begins = [] # saving everything in a list to show it in the dataframe
    service_ends = []
    waiting_times = []
    pumps = []

    for i in range(n_cars): # loop through all cars to simulate them
        category = categories[i]
        arrival = arrival_times[i]

        if category == "A":
            selected_pump = "95"
        elif category == "B":
            if len(pump_queues["90"]) > 3 and random.random() <= 0.6:
                selected_pump = "95"
            else:
                selected_pump = "90"
        else:
            if len(pump_queues["Gas"]) > 4 and random.random() <= 0.4:
                selected_pump = "90"
            else:
                selected_pump = "Gas"

        # Remove cars that have already finished service
        pump_queue = pump_queues[selected_pump]
        pump_queues[selected_pump] = [(starting, ending) for starting, ending in pump_queue if ending > arrival]
        current_queue_length[selected_pump] = len(pump_queues[selected_pump])  # Update current queue length

        start_time = max(arrival, pump_queue[-1][1] if pump_queue else 0)
        end_time = start_time + service_times[i]
        waiting_time = max(0, start_time - arrival)

        service_begins.append(start_time)
        service_ends.append(end_time)
        waiting_times.append(waiting_time)
        pumps.append(selected_pump)

        pump_queues[selected_pump].append((start_time, end_time))  # Add the car to the queue
        current_queue_length[selected_pump] += 1  # Increment the current queue length
        max_queue_length[selected_pump] = max(max_queue_length[selected_pump],
                                              current_queue_length[selected_pump])  # Update max queue length

        if start_time > last_end_time[selected_pump]:
            pump_idle_times[selected_pump] += start_time - last_end_time[selected_pump]

        last_end_time[selected_pump] = end_time

    simulation_end_time = max(service_ends)
    for pump in pump_idle_times:
        if last_end_time[pump] < simulation_end_time:
            pump_idle_times[pump] += simulation_end_time - last_end_time[pump]

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

    avg_service_time = {}
    for category in ["A", "B", "C"]:
        avg_service_time[category] = round(data[data["Category"] == category]["Service Time"].mean(), 2)

    avg_waiting_time_per_pump = {}
    for pump in ["95", "90", "Gas"]:
        avg_waiting_time_per_pump[pump] = round(data[data["Pump"] == pump]["Waiting Time"].mean(), 2)

    overall_avg_waiting_time = round(data["Waiting Time"].mean(), 2)

    idle_time_ratios = {}
    for pump in pump_idle_times:
        idle_time_ratios[pump] = pump_idle_times[pump] 

    max_queue_lengths = max_queue_length

    waiting_probabilities = {}
    for pump in pump_queues:
        total_cars_at_pump = len(data[data["Pump"] == pump])
        cars_that_waited = len(data[(data["Pump"] == pump) & (data["Waiting Time"] > 0)])
        waiting_probabilities[pump] = round(cars_that_waited / total_cars_at_pump if total_cars_at_pump > 0 else 0, 2)


    th_avg_service = {}
    th_avg_service["A"] = round(1 * 0.2 + 2 * 0.3 + 3 * 0.5, 2) # theoretical average service time for category A
    th_avg_service["B"] = round(1 * 0.2 + 2 * 0.3 + 3 * 0.5, 2)
    th_avg_service["C"] = round(3 * 0.2 + 5 * 0.5 + 7 * 0.3, 2)
    th_avg_inter_time = round(0 * 0.17 + 1 * 0.23 + 2 * 0.25 + 3 * 0.35, 2) 

    #bnshoof law zawedna extra pump waiting time hayt2asar ezay
    add_wait_times = {}
    for pump in ["95", "90", "Gas"]:
        reduced_waiting_times = []
        for index, row in data.iterrows(): #variabble index input data.itterows yzbot
            if row["Pump"] == pump:
                reduced_waiting_times.append(max(0, row["Waiting Time"] - 1)) 
            else:
                reduced_waiting_times.append(row["Waiting Time"])
        add_wait_times[pump] = round(sum(reduced_waiting_times) / len(reduced_waiting_times), 2)

    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, data)
    results_text.insert(tk.END, "\n\nStatistics:\n")
    results_text.insert(tk.END, "1. Average Service Time per Category:\n")
    for category, avg_time in avg_service_time.items():
        results_text.insert(tk.END, f"   {category}: {avg_time}\n")
    results_text.insert(tk.END, "\n2. Average Waiting Time per Pump:\n")
    for pump, avg_time in avg_waiting_time_per_pump.items():
        results_text.insert(tk.END, f"   {pump}: {avg_time}\n")
    results_text.insert(tk.END, f"   Overall Average Waiting Time: {overall_avg_waiting_time}\n")
    results_text.insert(tk.END, "\n3. Maximum Queue Lengths:\n")
    for pump, length in max_queue_lengths.items():
        results_text.insert(tk.END, f"   {pump}: {length}\n")
    results_text.insert(tk.END, "\n4. Waiting Probabilities per Pump:\n")
    for pump, prob in waiting_probabilities.items():
        results_text.insert(tk.END, f"   {pump}: {prob}\n")
    results_text.insert(tk.END, "\n5. Idle Time :\n")
    for pump, ratio in idle_time_ratios.items():
        results_text.insert(tk.END, f"   {pump}: {ratio}\n")
    results_text.insert(tk.END, "\nPolicy Questions:\n")
    results_text.insert(tk.END, "6. Theoretical vs Experimental Average Service Time per Category:\n")
    for category in avg_service_time:
        results_text.insert(tk.END, f"   Category {category}: Theoretical = {th_avg_service[category]}, Experimental = {avg_service_time[category]}\n")
    results_text.insert(tk.END, "7. Theoretical vs Experimental Average Inter-Arrival Time:\n")
    exp_avg_inter_time = round(sum(inter_arrival_times) / len(inter_arrival_times), 2)
    results_text.insert(tk.END, f"   Theoretical = {th_avg_inter_time}, Experimental = {exp_avg_inter_time}\n")
    results_text.insert(tk.END, "8. Effect of Adding Extra Pump:\n")
    for pump, avg_time in add_wait_times.items():
        results_text.insert(tk.END, f"   Adding an extra {pump} pump reduces average waiting time to {avg_time}\n")

#  global variable to store results of all runs
all_runs_data = []


def run_multiple_simulations():
    global all_runs_data
    all_runs_data = []  # Reset kol mara
    num_runs = int(num_runs_entry.get())

    for run in range(1, num_runs + 1):
        run_simulation()
        all_runs_data.append(data.copy())
        if not os.path.exists(".\\Petrol Station\\Simulation_Results"): #e3ml folder w ermyhom fyh
            os.makedirs(".\\Petrol Station\\Simulation_Results")
        with open(f".\\Petrol Station\\Simulation_Results\\Run_{run}_Results.txt", "w") as file:
            file.write(data.to_string())       
    
    calculate_average_across_runs(num_runs)


def calculate_average_across_runs(num_runs):
    global all_runs_data
    concatenated_data = pd.concat(all_runs_data, ignore_index=True)

    # Average Service Time per Category
    avg_service_time = concatenated_data.groupby("Category")["Service Time"].mean().round(2)
    # Average Waiting Time per Pump
    avg_waiting_time_per_pump = concatenated_data.groupby("Pump")["Waiting Time"].mean().round(2)
    # Overall Average Waiting Time
    overall_avg_waiting_time = concatenated_data["Waiting Time"].mean().round(2)


    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, "Averages Across All Runs:\n")
    results_text.insert(tk.END, "1. Average Service Time per Category:\n")
    for category, avg_time in avg_service_time.items():
        results_text.insert(tk.END, f"   {category}: {avg_time}\n")
    results_text.insert(tk.END, "\n2. Average Waiting Time per Pump:\n")
    for pump, avg_time in avg_waiting_time_per_pump.items():
        results_text.insert(tk.END, f"   {pump}: {avg_time}\n")
    results_text.insert(tk.END, f"   Overall Average Waiting Time: {overall_avg_waiting_time}\n")
    results_text.insert(tk.END, f"\nResults of all runs have been saved as Run_<RunNumber>_Results.txt files.")

# plot histograms
def plot_histograms():
    for pump in ["95", "90", "Gas"]:
        pump_data = data[data["Pump"] == pump]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

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

        plt.tight_layout()
        plt.show()

#GUIIII
root = tk.Tk()
root.title("Gas Station Simulation")
root.configure(bg="#2E2E2E") 


tk.Label(root, text="Number of Cars:", bg="#2E2E2E", fg="#F2F2F2").grid(row=0, column=0, padx=10, pady=10)
num_cars_entry = tk.Entry(root, bg="#4F4F4F", fg="#F2F2F2", insertbackground="#F2F2F2")
num_cars_entry.grid(row=0, column=1, padx=10, pady=10)


start_button = tk.Button(
    root, text="Start Simulation", bg="#4F4F4F", fg="#F2F2F2", activebackground="#6E6E6E", activeforeground="#F2F2F2", command=run_simulation
)
start_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)


plot_button = tk.Button(
    root, text="Plot Histograms", bg="#4F4F4F", fg="#F2F2F2", activebackground="#6E6E6E", activeforeground="#F2F2F2", command=plot_histograms
)
plot_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)


results_text = scrolledtext.ScrolledText(
    root, bg="#2E2E2E", fg="#F2F2F2", insertbackground="#F2F2F2", width=100, height=30
)
results_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)


def plot_averages(num_runs):  #variable num_runs used later in lambda
    global all_runs_data
    concatenated_data = pd.concat(all_runs_data, ignore_index=True) #concatenate all runs to get the averages

    avg_service_time = concatenated_data.groupby("Category")["Service Time"].mean().round(2)
    std_service_time = concatenated_data.groupby("Category")["Service Time"].std().round(2) #standard deviation
    avg_waiting_time = concatenated_data.groupby("Pump")["Waiting Time"].mean().round(2)
    std_waiting_time = concatenated_data.groupby("Pump")["Waiting Time"].std().round(2)

  # bar charrts
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Average Service Time Plot
    axes[0].bar(avg_service_time.index, avg_service_time, yerr=std_service_time, capsize=5, color='skyblue', edgecolor='blue')
    axes[0].set_title("Average Service Time per Category")
    axes[0].set_xlabel("Car Category")
    axes[0].set_ylabel("Average Service Time (minutes)")

    # Average Waiting Time Plot
    axes[1].bar(avg_waiting_time.index, avg_waiting_time, yerr=std_waiting_time, capsize=5, color='lightcoral', edgecolor='red')
    axes[1].set_title("Average Waiting Time per Pump")
    axes[1].set_xlabel("Pump Type")
    axes[1].set_ylabel("Average Waiting Time (minutes)")

    plt.tight_layout()
    plt.show()



tk.Label(root, text="Number of Runs:", bg="#2E2E2E", fg="#F2F2F2").grid(row=0, column=2, padx=10, pady=10)
num_runs_entry = tk.Entry(root, bg="#4F4F4F", fg="#F2F2F2", insertbackground="#F2F2F2")
num_runs_entry.grid(row=0, column=3, padx=10, pady=10)
visualize_button = tk.Button(
    root, text="Visualize Averages", bg="#4F4F4F", fg="#F2F2F2", activebackground="#6E6E6E", activeforeground="#F2F2F2", command=lambda: plot_averages(int(num_runs_entry.get()))
)
visualize_button.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

multi_run_button = tk.Button(
    root, text="Run Multiple Simulations", bg="#4F4F4F", fg="#F2F2F2", activebackground="#6E6E6E", activeforeground="#F2F2F2", command=run_multiple_simulations
)
multi_run_button.grid(row=1, column=2, columnspan=2, padx=10, pady=10)


root.mainloop()
