# Created by Colin Mckay on April 18. 2025.


import tkinter as tk
from tkinter import ttk
import psutil
import platform
import socket
import os
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import shutil


class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AquaSys Monitor")
        self.root.geometry("1440x1080")
        self.root.configure(bg="#0f2c2c")

        style = ttk.Style()
        style.configure("TFrame", background="#0f2c2c")
        style.configure("TButton", padding=6, relief="flat", background="#00ffe7")

        self.main_canvas = tk.Canvas(root, bg="#0f2c2c", highlightthickness=0)
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

        self.title_label = tk.Label(self.scrollable_frame, text="System Resource Monitor", font=("Arial", 20, "bold"),
                                    fg="#00ffe7", bg="#0f2c2c")
        self.title_label.pack(pady=10)

        self.top_frame = tk.Frame(self.scrollable_frame, bg="#0f2c2c")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.log_frame = tk.Frame(self.top_frame, bg="#0f2c2c", highlightbackground="white", highlightthickness=2)
        self.log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_box = tk.Text(self.log_frame, height=15, width=90, bg="#001f1f", fg="white", font=("Courier", 10),
                               relief="flat", bd=5, highlightbackground="#00ffe7", highlightthickness=1)
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

        self.graph_frame = tk.Frame(self.scrollable_frame, bg="#0f2c2c")
        self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.cpu_mem_frame = tk.Frame(self.graph_frame, bg="#0f2c2c", highlightbackground="white", highlightthickness=2)
        self.cpu_mem_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

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

        self.disk_frame = tk.Frame(self.graph_frame, bg="#0f2c2c", highlightbackground="white", highlightthickness=2)
        self.disk_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.disk_label = tk.Label(self.disk_frame, text="Disk Usage: Calculating...", font=("Arial", 12), fg="#00ffe7",
                                   bg="#0f2c2c")
        self.disk_label.pack(pady=5)

        self.temp_frame = tk.Frame(self.graph_frame, bg="#0f2c2c", highlightbackground="white", highlightthickness=2)
        self.temp_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.temp_label = tk.Label(self.temp_frame, text="CPU Temperature: Simulating...", font=("Arial", 12),
                                   fg="#00ffe7", bg="#0f2c2c")
        self.temp_label.pack(pady=5)

        self.cpu_data = []
        self.mem_data = []
        self.timestamps = []

        self.update_data()

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

        self.cpu_data.append(cpu)
        self.mem_data.append(mem)
        self.timestamps.append(current_time)

        max_points = 20
        self.cpu_data = self.cpu_data[-max_points:]
        self.mem_data = self.mem_data[-max_points:]
        self.timestamps = self.timestamps[-max_points:]

        self.cpu_usage.set_data(range(len(self.cpu_data)), self.cpu_data)
        self.mem_usage.set_data(range(len(self.mem_data)), self.mem_data)

        self.ax[0].set_xlim(0, len(self.cpu_data) - 1)
        self.ax[0].set_ylim(0, 100)
        self.ax[1].set_xlim(0, len(self.mem_data) - 1)
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


if "__main__" == __name__:
    root = tk.Tk()
    try:
        app = SystemMonitorApp(root)
        root.mainloop()
    except Exception as e:
        print("Error initializing application:", e)
