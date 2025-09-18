import tkinter as tk
from tkinter import ttk
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv

# PID constants
Kp = 1.0  # Proportional gain
Ki = 0.1  # Integral gain
Kd = 0.05 # Derivative gain

# Control output limits (represent throttle %)
max_output = 100.0 
min_output = 0.0  

# Global variables
setpoint = 50.0  # Target speed in km/h (car speed target)
integral = 0.0
last_error = 0.0
current_value = 0.0  # Starting car speed (km/h)
previous_measurement = 0.0  # For derivative filtering
car_position = 10  # Initial car position on the canvas

# Lists to store data for plotting
time_data = []
current_value_data = []
setpoint_data = []
control_output_data = []
rise_time_data = []

# PID controller function
def pid_controller(current_value, setpoint):
    global integral, last_error, previous_measurement
    
    # Calculate the error (target speed - current speed)
    error = setpoint - current_value
    
    # Proportional term
    proportional = Kp * error
    
    # Integral term (accumulate error over time)
    integral += error
    
    # Derivative term with noise filtering (Low-pass filter on derivative)
    derivative = Kd * (current_value - previous_measurement)
    previous_measurement = current_value
    
    # Compute the PID output (throttle percentage)
    control_output = proportional + (Ki * integral) + derivative
    
    # Apply output limits (Throttle between 0-100%)
    control_output = max(min(control_output, max_output), min_output)
    
    # Anti-windup: Adjust the integral if output is saturated
    if control_output == max_output or control_output == min_output:
        integral -= error  # Prevent further accumulation when saturated
    
    return control_output

# Simulate the process (car speed dynamics)
def simulate_process(stop_event):
    global current_value, car_position
    
    start_time = time.time()
    
    while not stop_event.is_set():
        # Simulate a process that responds to the control output (Throttle input)
        control_output = pid_controller(current_value, setpoint)
        
        # Simulate the effect of throttle on car speed, and add friction/resistance
        friction = 0.1 * current_value  # Simulated resistance (friction)
        noise = np.random.normal(0, 0.2)  # Add some noise to simulate disturbances
        
        # Update car speed: increase with control output, decrease with friction
        current_value += (control_output * 0.2) - friction + noise
        
        # Move the car position based on speed (control output)
        car_position += control_output * 0.1  # Change in position per unit time
        
        # Append data for graphing
        elapsed_time = time.time() - start_time
        time_data.append(elapsed_time)
        current_value_data.append(current_value)
        setpoint_data.append(setpoint)
        control_output_data.append(control_output)
        
        # Limit the data to the last 100 points to keep the graph responsive
        if len(time_data) > 100:
            time_data.pop(0)
            current_value_data.pop(0)
            setpoint_data.pop(0)
            control_output_data.pop(0)
        
        # Update the graph and the car diagram
        update_graph()
        update_car_diagram()
        
        # Pause to simulate a sampling interval
        time.sleep(0.1)

# Update the graph in real-time
def update_graph():
    ax1.clear()
    ax1.plot(time_data, current_value_data, label="Car Speed (km/h)", color="blue")
    ax1.plot(time_data, setpoint_data, label="Target Speed", color="green", linestyle="dashed")
    ax1.set_title("Car Speed vs Target Speed")
    ax1.set_ylabel("Speed (km/h)")
    ax1.legend(loc="upper left")
    
    ax2.clear()
    ax2.plot(time_data, control_output_data, label="Throttle (Control Output)", color="red")
    ax2.set_title("Throttle (Control Output) vs Time")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Throttle (%)")
    ax2.legend(loc="upper left")
    
    # Display performance metrics
    steady_state_error = setpoint - current_value if time_data else 0
    overshoot = max(current_value_data) - setpoint if current_value_data else 0
    rise_time = get_rise_time()
    
    metrics_label["text"] = (f"Steady-State Error: {steady_state_error:.2f} km/h\n"
                             f"Overshoot: {overshoot:.2f} km/h\n"
                             f"Rise Time: {rise_time:.2f} s")

    canvas.draw()

def get_rise_time():
    # Example: Calculate rise time (time to reach 90% of setpoint)
    if len(current_value_data) > 1:
        for i, value in enumerate(current_value_data):
            if value >= setpoint * 0.9:
                return time_data[i]
    return 0.0

# Update the car diagram based on the car position
def update_car_diagram():
    global car_position
    
    # Clear the canvas
    canvas_car.delete("all")
    
    # Draw the road (a simple line from left to right)
    canvas_car.create_line(0, 180, 800, 180, fill="gray", width=5)
    
    # Define the car's size and position based on the car_position variable
    car_width = 150  # Make the car width bigger
    car_height = 60  # Increase the car height for a larger diagram
    car_x = car_position  # Position the car horizontally based on car_position
    
    # Car body
    canvas_car.create_rectangle(car_x, 160, car_x + car_width, 160 + car_height, fill="blue", outline="black")
    
    # Wheels (two wheels for simplicity)
    wheel_radius = 15  # Make the wheels a bit larger for the bigger car
    wheel_y = 160 + car_height - 5
    
    # Left wheel
    canvas_car.create_oval(car_x + 20, wheel_y, car_x + 20 + wheel_radius, wheel_y + wheel_radius, fill="black")
    
    # Right wheel
    canvas_car.create_oval(car_x + car_width - 20 - wheel_radius, wheel_y, car_x + car_width - 20, wheel_y + wheel_radius, fill="black")
    
    # Update the canvas
    canvas_car.update()

# Start/stop simulation
def toggle_simulation():
    if start_button["text"] == "Start":
        # Start the simulation
        start_button["text"] = "Stop"
        stop_event.clear()
        threading.Thread(target=simulate_process, args=(stop_event,), daemon=True).start()
    else:
        # Stop the simulation
        start_button["text"] = "Start"
        stop_event.set()

# Adjust PID parameters
def update_pid():
    global Kp, Ki, Kd, setpoint
    Kp = float(kp_entry.get())
    Ki = float(ki_entry.get())
    Kd = float(kd_entry.get())
    setpoint = float(setpoint_entry.get())

# Save data to CSV
def save_to_csv():
    filename = "car_speed_pid_simulation_data.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "Car Speed (km/h)", "Setpoint", "Throttle"])
        for t, cv, sp, co in zip(time_data, current_value_data, setpoint_data, control_output_data):
            writer.writerow([t, cv, sp, co])
    print(f"Data saved to {filename}")

# Create the GUI
root = tk.Tk()
root.title("Car Speed PID Controller Simulation")

# Create frames
control_frame = ttk.Frame(root, padding="10")
control_frame.grid(row=0, column=0, sticky="nsew")
graph_frame = ttk.Frame(root)
graph_frame.grid(row=0, column=1, sticky="nsew")

# Make the graph frame take more space
root.grid_columnconfigure(0, weight=1, minsize=300)  # Control frame
root.grid_columnconfigure(1, weight=3, minsize=600)  # Graph frame (larger)

# Title for Control Panel
title_label = ttk.Label(control_frame, text="PID Controller Settings", font=("Arial", 14, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Control panel labels and inputs with improved styling
ttk.Label(control_frame, text="Target Speed (km/h):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
setpoint_entry = ttk.Entry(control_frame, width=15)
setpoint_entry.grid(row=1, column=1, padx=5, pady=5)
setpoint_entry.insert(0, "50.0")

ttk.Label(control_frame, text="Kp:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
kp_entry = ttk.Entry(control_frame, width=15)
kp_entry.grid(row=2, column=1, padx=5, pady=5)
kp_entry.insert(0, "1.0")

ttk.Label(control_frame, text="Ki:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
ki_entry = ttk.Entry(control_frame, width=15)
ki_entry.grid(row=3, column=1, padx=5, pady=5)
ki_entry.insert(0, "0.1")

ttk.Label(control_frame, text="Kd:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
kd_entry = ttk.Entry(control_frame, width=15)
kd_entry.grid(row=4, column=1, padx=5, pady=5)
kd_entry.insert(0, "0.05")

update_button = ttk.Button(control_frame, text="Update PID", command=update_pid, width=20)
update_button.grid(row=5, column=0, columnspan=2, pady=10)

start_button = ttk.Button(control_frame, text="Start", command=toggle_simulation, width=20)
start_button.grid(row=6, column=0, columnspan=2, pady=10)

save_button = ttk.Button(control_frame, text="Save to CSV", command=save_to_csv, width=20)
save_button.grid(row=7, column=0, columnspan=2, pady=10)

# Performance Metrics
metrics_label = ttk.Label(control_frame, text="Metrics", justify="left", font=("Arial", 10), relief="sunken", padding=10)
metrics_label.grid(row=8, column=0, columnspan=2, pady=10)

# Graph panel
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Larger size for the graph
fig.tight_layout(pad=3.0)
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, sticky="nsew")

graph_frame.grid_rowconfigure(0, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)

# Car Diagram (Canvas for car position)
car_frame = ttk.Frame(root, padding="10")
car_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

canvas_car = tk.Canvas(car_frame, width=900, height=300, bg="white")
canvas_car.grid(row=0, column=0)

stop_event = threading.Event()

root.mainloop()
