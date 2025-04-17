# Made by Colin Mckay on April 18, 2025.

import tkinter as tk
from tkinter import ttk
import psutil
import platform
import socket
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AquaSys Monitor")
        self.root.geometry("1440x1080")
        self.root.configure(bg="#0f2c2c")

        # Main scrollable canvas
        self.main_canvas = tk.Canvas(root, bg="#0f2c2c")
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#0f2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Title
        self.title_label = tk.Label(self.scrollable_frame, text="System Resource Monitor", font=("Arial", 20, "bold"),
                                    fg="#00ffe7", bg="#0f2c2c")
        self.title_label.pack(pady=10)

        # Top section for logs and system info
        self.top_frame = tk.Frame(self.scrollable_frame, bg="#0f2c2c")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.log_frame = tk.Frame(self.top_frame, bg="#0f2c2c", highlightbackground="white", highlightthickness=2)
        self.log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_box = tk.Text(self.log_frame, height=15, width=90, bg="#001f1f", fg="white", font=("Courier", 10))
        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.info_frame = tk.Frame(self.top_frame, bg="#001f1f", highlightbackground="white", highlightthickness=2)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10, pady=5)

        self.sys_info_label = tk.Label(self.info_frame, text="System Info", font=("Arial", 12, "bold"), fg="#00ffe7",
                                       bg="#001f1f")
        self.sys_info_label.pack(anchor="w", padx=10, pady=(10, 0))

        sys_info = self.get_system_info()
        for key, value in sys_info.items():
            tk.Label(self.info_frame, text=f"{key}: {value}", font=("Arial", 10), fg="white", bg="#001f1f").pack(
                anchor="w", padx=10)

        # Add colored buttons for displaying more information
        self.button_frame = tk.Frame(self.scrollable_frame, bg="#0f2c2c")
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.create_colored_button("CPU Info", self.show_cpu_info)
        self.create_colored_button("Memory Info", self.show_mem_info)
        self.create_colored_button("Disk Info", self.show_disk_info)
        self.create_colored_button("Temperature Info", self.show_temp_info)

        # Graph section
        self.graph_frame = tk.Frame(self.scrollable_frame, bg="#0f2c2c")
        self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.cpu_mem_frame = tk.Frame(self.graph_frame, bg="#0f2c2c", highlightbackground="white", highlightthickness=2)
        self.cpu_mem_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create matplotlib figure with 2 subplots
        self.fig, self.ax = plt.subplots(2, 1, figsize=(8, 5), facecolor="#0f2c2c")
        self.fig.subplots_adjust(hspace=0.6)
        self.cpu_usage, = self.ax[0].plot([], [], color='#00ffe7', label="CPU Usage")
        self.mem_usage, = self.ax[1].plot([], [], color='#00ffa2', label="Memory Usage")

        for a in self.ax:
            a.set_facecolor("#001f1f")
            a.grid(True, linestyle='--', alpha=0.3)
            a.tick_params(axis='x', colors='white')
            a.tick_params(axis='y', colors='white')
            a.title.set_color('white')

        self.ax[0].set_title("CPU Usage (%)")
        self.ax[0].legend(loc="upper right")
        self.ax[1].set_title("Memory Usage (%)")
        self.ax[1].legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.cpu_mem_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Data containers
        self.cpu_data = []
        self.mem_data = []
        self.timestamps = []

        # Add disk_label for displaying disk usage
        self.disk_label = tk.Label(self.scrollable_frame, text="Disk Usage: N/A", font=("Arial", 12), fg="white",
                                   bg="#0f2c2c")
        self.disk_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.temp_label = tk.Label(self.scrollable_frame, text="CPU Temperature: N/A", font=("Arial", 12), fg="white",
                                   bg="#0f2c2c")
        self.temp_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.update_data()

    def create_colored_button(self, text, command):
        button = tk.Button(self.button_frame, text=text, command=command, bg="white", fg="black",
                           font=("Arial", 12, "bold"), relief="solid", bd=2)
        button.pack(side=tk.LEFT, padx=10, pady=5)

    def get_system_info(self):
        return {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "RAM Size": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB"
        }

    def update_data(self):
        current_time = time.strftime('%H:%M:%S')
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        temp = entries[0].current
                        break
                    else:
                        temp = 'N/A'
            else:
                temp = 'N/A'
        except:
            temp = 45 + (cpu / 100) * 30

        # Append new data for average calculation
        self.cpu_data.append(cpu)
        self.mem_data.append(mem)
        self.timestamps.append(current_time)

        # Keep data length manageable
        max_points = 20
        self.cpu_data = self.cpu_data[-max_points:]
        self.mem_data = self.mem_data[-max_points:]
        self.timestamps = self.timestamps[-max_points:]

        # Update graph data
        self.cpu_usage.set_data(range(len(self.cpu_data)), self.cpu_data)
        self.mem_usage.set_data(range(len(self.mem_data)), self.mem_data)

        # Fix for the xlim warning: set limits only if there are enough data points
        if len(self.cpu_data) > 1:
            self.ax[0].set_xlim(0, len(self.cpu_data) - 1)
            self.ax[1].set_xlim(0, len(self.mem_data) - 1)
        else:
            self.ax[0].set_xlim(0, 1)
            self.ax[1].set_xlim(0, 1)

        self.ax[0].set_ylim(0, 100)
        self.ax[1].set_ylim(0, 100)

        self.ax[0].set_xticks(range(len(self.timestamps)))
        self.ax[0].set_xticklabels(self.timestamps, rotation=45, ha="right")
        self.ax[1].set_xticks(range(len(self.timestamps)))
        self.ax[1].set_xticklabels(self.timestamps, rotation=45, ha="right")

        self.canvas.draw()

        avg_cpu = sum(self.cpu_data) / len(self.cpu_data)
        avg_mem = sum(self.mem_data) / len(self.mem_data)

        self.disk_label.config(text=f"Disk Usage: {disk}%")
        self.temp_label.config(text=f"CPU Temperature: {temp:.1f} °C, Avg CPU: {avg_cpu:.1f}%")

        self.log_box.insert(tk.END,
                            f"[{current_time}] CPU: {cpu}% (Avg: {avg_cpu:.1f}%) | Memory: {mem}% (Avg: {avg_mem:.1f}%) | Disk: {disk}% | Temp: {temp:.1f}°C\n")
        self.log_box.see(tk.END)

        self.root.after(1000, self.update_data)

    def show_cpu_info(self):
        self.log_box.insert(tk.END, "[INFO] CPU Information:\n")
        cpu_info = psutil.cpu_freq()
        self.log_box.insert(tk.END, f"  - Current Frequency: {cpu_info.current} MHz\n")
        self.log_box.insert(tk.END, f"  - Min Frequency: {cpu_info.min} MHz\n")
        self.log_box.insert(tk.END, f"  - Max Frequency: {cpu_info.max} MHz\n")
        self.log_box.insert(tk.END, f"  - CPU Count: {psutil.cpu_count(logical=False)} (Physical cores)\n")
        self.log_box.insert(tk.END, f"  - Logical CPUs: {psutil.cpu_count(logical=True)}\n")
        self.log_box.see(tk.END)

    def show_mem_info(self):
        self.log_box.insert(tk.END, "[INFO] Memory Information:\n")
        mem_info = psutil.virtual_memory()
        self.log_box.insert(tk.END, f"  - Total Memory: {mem_info.total / (1024 ** 3):.2f} GB\n")
        self.log_box.insert(tk.END, f"  - Available Memory: {mem_info.available / (1024 ** 3):.2f} GB\n")
        self.log_box.insert(tk.END, f"  - Used Memory: {mem_info.used / (1024 ** 3):.2f} GB\n")
        self.log_box.insert(tk.END, f"  - Memory Usage: {mem_info.percent}%\n")
        self.log_box.see(tk.END)

    def show_disk_info(self):
        self.log_box.insert(tk.END, "[INFO] Disk Information:\n")
        disk_info = psutil.disk_usage('/')
        self.log_box.insert(tk.END, f"  - Total Space: {disk_info.total / (1024 ** 3):.2f} GB\n")
        self.log_box.insert(tk.END, f"  - Used Space: {disk_info.used / (1024 ** 3):.2f} GB\n")
        self.log_box.insert(tk.END, f"  - Free Space: {disk_info.free / (1024 ** 3):.2f} GB\n")
        self.log_box.insert(tk.END, f"  - Disk Usage: {disk_info.percent}%\n")
        self.log_box.see(tk.END)

    def show_temp_info(self):
        self.log_box.insert(tk.END, "[INFO] Temperature Information:\n")
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    self.log_box.insert(tk.END, f"  - {name} sensor: {entries[0].current}°C\n")
        else:
            self.log_box.insert(tk.END, "  - Temperature data unavailable.\n")
        self.log_box.see(tk.END)


if "__main__" == __name__:
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()
