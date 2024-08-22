import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psutil
import pygetwindow as gw
import time
from datetime import datetime
import csv
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Dictionary to store time spent on each app
usage_data = {}

# Tkinter setup
root = tk.Tk()
root.title("App Usage Tracker")

# Create the main frame
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Add a label to show the status
status_label = tk.Label(frame, text="Tracking is OFF", font=("Helvetica", 12))
status_label.pack(pady=5)

# Add a table to display usage data
columns = ["App Name", "Time Spent (seconds)"]
tree = ttk.Treeview(frame, columns=columns, show="headings")
tree.heading("App Name", text="App Name")
tree.heading("Time Spent (seconds)", text="Time Spent (seconds)")
tree.pack()

# Add a canvas for charts
chart_frame = tk.Frame(root)
chart_frame.pack(padx=10, pady=10)
chart_label = tk.Label(chart_frame, text="App Usage Chart", font=("Helvetica", 12))
chart_label.pack(pady=5)

def get_active_window_title():
    try:
        window = gw.getActiveWindow()
        return window.title if window else None
    except Exception as e:
        print(f"Error getting active window: {e}")
        return None

def log_app_usage():
    active_window = get_active_window_title()
    if active_window:
        current_time = datetime.now()
        
        if active_window in usage_data:
            usage_data[active_window]['duration'] += (current_time - usage_data[active_window]['last_used']).total_seconds()
        else:
            usage_data[active_window] = {'duration': 0, 'last_used': current_time}

        usage_data[active_window]['last_used'] = current_time

def update_treeview():
    for item in tree.get_children():
        tree.delete(item)
    for app, data in usage_data.items():
        tree.insert("", "end", values=[app, round(data['duration'], 2)])

def save_data_to_csv():
    with open('app_usage_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["App Name", "Time Spent (seconds)"])
        for app, data in usage_data.items():
            writer.writerow([app, data['duration']])

def visualize_data():
    apps = list(usage_data.keys())
    durations = [data['duration'] / 60 for data in usage_data.values()]  # Convert seconds to minutes

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(apps, durations, color='skyblue')
    ax.set_xlabel('Time Spent (minutes)')
    ax.set_title('Time Spent on Applications')

    # Clear the previous chart if any
    for widget in chart_frame.winfo_children():
        widget.destroy()

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def start_tracking():
    status_label.config(text="Tracking is ON")
    global tracking
    tracking = True
    tracking_thread = threading.Thread(target=track_usage)
    tracking_thread.start()

def stop_tracking():
    global tracking
    tracking = False
    status_label.config(text="Tracking is OFF")
    save_data_to_csv()
    update_treeview()
    visualize_data()

def track_usage():
    while tracking:
        log_app_usage()
        root.after(5000, update_treeview)  # Schedule GUI update
        time.sleep(5)  # Sleep for 5 seconds

def show_about():
    messagebox.showinfo("About", "App Usage Tracker v1.0\nDeveloped by m11ne")

# Initialize tracking status
tracking = False

# Add Start, Stop, and About buttons
start_button = tk.Button(frame, text="Start Tracking", command=start_tracking)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(frame, text="Stop Tracking", command=stop_tracking)
stop_button.pack(side=tk.LEFT, padx=5)

about_button = tk.Button(frame, text="About", command=show_about)
about_button.pack(side=tk.RIGHT, padx=5)

root.mainloop()
