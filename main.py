import tkinter as tk
import subprocess
import os

# Function to run the Multichannel Queue project
def run_multichannel_queue():
      subprocess.run(["python", ".\\Petrol Station\\src.py"])
# Function to run the Inventory project
def run_inventory():
    subprocess.run(["python", ".\\Hospital Inventory System\\HospitalInventory.py"])

# Function to exit the application
def exit_app():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Simulation Project")

# Set the window size
root.geometry("600x400")

# Add a title label
title_label = tk.Label(root, text="Select a Simulation Project", font=("Arial", 16))
title_label.pack(pady=5)

# Load images using tkinter's PhotoImage with full path
queue_image_path = os.path.join('./', "img.gif")
inventory_image_path = os.path.join('./', "img1.gif")

queue_photo = tk.PhotoImage(file=queue_image_path)  # Load the first image
inventory_photo = tk.PhotoImage(file=inventory_image_path)  # Load the second image

# Create a frame for the buttons and images
frame = tk.Frame(root)
frame.pack(pady=5)

# Add button for Multichannel Queue project
queue_button = tk.Button(
    frame,
    text="Multichannel Queue (Petrol Station)",
    command=run_multichannel_queue,
    compound="top",  # Position the image above the text
    image=queue_photo if queue_photo else None,  # Use the image if loaded
    width=250,  # Button width
    height=270  # Button height
)
queue_button.grid(row=0, column=0, padx=5, pady=5)

# Add button for Inventory project
inventory_button = tk.Button(
    frame,
    text="Inventory (Hospital Basement Inventory)",
    command=run_inventory,
    compound="top",  # Position the image above the text
    image=inventory_photo if inventory_photo else None,  # Use the image if loaded
    width=250,  # Button width
    height=270  # Button height
)
inventory_button.grid(row=0, column=1, padx=5, pady=5)

# Add an exit button
exit_button = tk.Button(root, text="Exit", command=exit_app, width=20, height=2)
exit_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
