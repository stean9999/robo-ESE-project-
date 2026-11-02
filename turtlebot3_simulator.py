#!/usr/bin/env python3
"""
TurtleBot3 Autonomous Warehouse Navigation Simulator
Author: Senior ROS Developer
Designed for: LAB ESE Robotics Exam Demonstration

Simulates the complete ROS 1 Navigation Stack:
1. TurtleBot3 Burger Kinematics & Lidar rays
2. AMCL (Adaptive Monte Carlo Localization) Particle Filter
3. Initial Pose Setting (PoseWithCovarianceStamped to /initialpose)
4. move_base Action Client / Server with Active, Feedback, and Done callbacks
5. Sequential Multi-Station Warehouse Mission with 2-second dwell delays
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 640
SCALE = 100.0  # 1 meter = 100 pixels
OFFSET_X = CANVAS_WIDTH // 2
OFFSET_Y = CANVAS_HEIGHT // 2

def world_to_screen(wx, wy):
    """Converts metric world coordinates (ROS map frame) to canvas pixels."""
    sx = OFFSET_X + (wx * SCALE)
    sy = OFFSET_Y - (wy * SCALE)  # Screen Y is inverted
    return sx, sy

# Warehouse Obstacles in TurtleBot3 World (pillars & walls)
OBSTACLES = [
    # Center pillar
    {"type": "circle", "x": 0.0, "y": 0.0, "radius": 0.35, "name": "Center Pillar"},
    # Cylinders / Obstacles
    {"type": "circle", "x": -1.0, "y": -1.2, "radius": 0.3, "name": "Storage Pillar B"},
    {"type": "circle", "x": 1.1, "y": 0.8, "radius": 0.3, "name": "Storage Pillar C"},
    {"type": "circle", "x": -0.8, "y": 1.3, "radius": 0.25, "name": "Barrier"},
    {"type": "circle", "x": 1.2, "y": -1.4, "radius": 0.25, "name": "Safety Zone"},
]

# Warehouse Waypoint Locations
WAYPOINTS = [
    {"name": "Loading Dock",  "x": -1.8, "y": -0.5, "yaw": 0.0,   "task": "Loading warehouse pallets..."},
    {"name": "Shelf Area A",   "x": 0.5,  "y": 1.5,  "yaw": 1.57,  "task": "Placing inventory on rack A3..."},
    {"name": "Sorting Desk",   "x": 1.8,  "y": -1.0, "yaw": 3.14,  "task": "Scanning barcode items..."},
    {"name": "Charging Base",  "x": -0.5, "y": 0.5,  "yaw": -1.57, "task": "Docking and replenishing battery..."}
]

class TurtleBot3SimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TurtleBot3 Autonomous Navigation Simulator (ROS 1 auto_nav)")
        self.root.geometry("1100x720")
        self.root.configure(bg="#1e1e2e")

        # Robot State (ground truth)
        self.robot_x = -2.0
        self.robot_y = -0.5
        self.robot_yaw = 0.0
        self.robot_radius = 0.18  # meters (~Burger size)

        # Particle Filter (AMCL simulation)
        self.particles = []
        self.is_localized = False
        self.generate_random_particles(num=120)

        # Navigation State
        self.current_wp_index = -1
        self.is_navigating = False
        self.dwell_timer_active = False
        self.dwell_end_time = 0
        self.mission_completed = False
        self.path_trail = []

        # Build UI
        self.setup_ui()

        # Initial Welcome Log
        self.log("[SYSTEM] TurtleBot3 Gazebo & Navigation Simulator Initialized.")
        self.log("[INFO] Ready for LAB ESE demonstration.")
        self.log("[STATUS] AMCL Particle Filter: UNINITIALIZED (Dispersed).")

        # Bring window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(500, lambda: self.root.attributes('-topmost', False))

        # Start simulation loop (30 FPS)
        self.root.after(33, self.simulation_loop)

        # Auto-start autonomous mission automatically after 1.5 seconds!
        self.root.after(1500, self.auto_start_mission)

    def auto_start_mission(self):
        """Automatically begins the autonomous sequence upon launching."""
        self.log("[AUTO-START] Commencing full autonomous mission automatically...", "HEADER")
        self.start_full_mission()

    def setup_ui(self):
        # Main layout: Left (Canvas) | Right (ROS Terminal & Controls)
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- LEFT: Simulation Canvas ---
        canvas_card = tk.Frame(main_frame, bg="#181825", bd=2, relief=tk.GROOVE)
        canvas_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        title_lbl = tk.Label(canvas_card, text="🐢 Gazebo & RViz Map View (TurtleBot3 World)",
                             font=("Segoe UI", 12, "bold"), fg="#cdd6f4", bg="#181825", pady=6)
        title_lbl.pack()

        self.canvas = tk.Canvas(canvas_card, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#11111b",
                               highlightthickness=1, highlightbackground="#313244")
        self.canvas.pack(padx=8, pady=8)

        # Legend under canvas
        legend_frame = tk.Frame(canvas_card, bg="#181825")
        legend_frame.pack(fill=tk.X, padx=10, pady=4)
        
        self.create_legend_item(legend_frame, "#89b4fa", "TurtleBot3")
        self.create_legend_item(legend_frame, "#a6e3a1", "AMCL Particles")
        self.create_legend_item(legend_frame, "#f38ba8", "Obstacles")
        self.create_legend_item(legend_frame, "#fab387", "Waypoints")
        self.create_legend_item(legend_frame, "#94e2d5", "Planned Path")

        # --- RIGHT: Control Panel & ROS Terminal ---
        right_frame = tk.Frame(main_frame, bg="#1e1e2e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Buttons Card
        btn_card = tk.LabelFrame(right_frame, text=" 🎮 Mission Controls ", font=("Segoe UI", 10, "bold"),
                                 fg="#cdd6f4", bg="#181825", bd=1, relief=tk.SOLID)
        btn_card.pack(fill=tk.X, pady=(0, 10), ipady=6)

        btn_row1 = tk.Frame(btn_card, bg="#181825")
        btn_row1.pack(fill=tk.X, padx=10, pady=4)

        self.btn_run_all = tk.Button(btn_row1, text="🚀 1-Click Run Full Mission",
                                     font=("Segoe UI", 10, "bold"), bg="#a6e3a1", fg="#11111b",
                                     activebackground="#94e2d5", cursor="hand2", padx=10, pady=6,
                                     command=self.start_full_mission)
        self.btn_run_all.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_reset = tk.Button(btn_row1, text="🔄 Reset",
                                   font=("Segoe UI", 10), bg="#45475a", fg="#cdd6f4",
                                   activebackground="#585b70", cursor="hand2", padx=10, pady=6,
                                   command=self.reset_all)
        self.btn_reset.pack(side=tk.RIGHT, padx=(5, 0))

        btn_row2 = tk.Frame(btn_card, bg="#181825")
        btn_row2.pack(fill=tk.X, padx=10, pady=4)

        self.btn_initial_pose = tk.Button(btn_row2, text="📍 1. Publish Initial Pose (/initialpose)",
                                          font=("Segoe UI", 9, "bold"), bg="#89b4fa", fg="#11111b",
                                          cursor="hand2", pady=5, command=self.publish_initial_pose)
        self.btn_initial_pose.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_start_nav = tk.Button(btn_row2, text="🎯 2. Start Waypoint Navigator",
                                       font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b",
                                       cursor="hand2", pady=5, command=self.start_waypoint_nav)
        self.btn_start_nav.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        # Status Banner
        self.status_var = tk.StringVar(value="Status: Ready. Click '1-Click Run Full Mission' to begin.")
        status_bar = tk.Label(right_frame, textvariable=self.status_var,
                              font=("Consolas", 10, "bold"), fg="#f9e2af", bg="#313244",
                              anchor="w", padx=10, pady=6)
        status_bar.pack(fill=tk.X, pady=(0, 10))

        # Terminal Log Window
        log_card = tk.LabelFrame(right_frame, text=" 💻 ROS Node Terminal Output (/rosout) ",
                                 font=("Segoe UI", 10, "bold"), fg="#cdd6f4", bg="#181825",
                                 bd=1, relief=tk.SOLID)
        log_card.pack(fill=tk.BOTH, expand=True)

        self.terminal_text = tk.Text(log_card, bg="#11111b", fg="#a6adc8", insertbackground="#cdd6f4",
                                     font=("Consolas", 9), wrap=tk.WORD, bd=0, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(log_card, command=self.terminal_text.yview)
        self.terminal_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure Terminal Color Tags (use 'foreground' parameter for Tkinter text tags)
        self.terminal_text.tag_config("INFO", foreground="#89b4fa")
        self.terminal_text.tag_config("SUCCESS", foreground="#a6e3a1")
        self.terminal_text.tag_config("WARN", foreground="#f9e2af")
        self.terminal_text.tag_config("ERROR", foreground="#f38ba8")
        self.terminal_text.tag_config("CALLBACK", foreground="#cba6f7")
        self.terminal_text.tag_config("HEADER", foreground="#fab387", font=("Consolas", 9, "bold"))

    def create_legend_item(self, parent, color, text):
        f = tk.Frame(parent, bg="#181825")
        f.pack(side=tk.LEFT, expand=True)
        c = tk.Canvas(f, width=12, height=12, bg="#181825", highlightthickness=0)
        c.pack(side=tk.LEFT, padx=3)
        c.create_oval(1, 1, 11, 11, fill=color, outline="")
        lbl = tk.Label(f, text=text, font=("Segoe UI", 8), fg="#a6adc8", bg="#181825")
        lbl.pack(side=tk.LEFT)

    def log(self, message, tag="INFO"):
        """Appends formatted timestamped message to terminal."""
        ts = time.strftime("%H:%M:%S")
        formatted = f"[{ts}] {message}\n"
        
        # Auto-detect tags
        if "CALLBACK" in message:
            tag = "CALLBACK"
        elif "SUCCESS" in message or "REACHED" in message or "Completed" in message:
            tag = "SUCCESS"
        elif "WARN" in message:
            tag = "WARN"
        elif "ERR" in message or "ABORT" in message:
            tag = "ERROR"
        elif "===" in message:
            tag = "HEADER"

        self.terminal_text.insert(tk.END, formatted, tag)
        self.terminal_text.see(tk.END)

    # ==========================
    # AMCL Particle Simulation
    # ==========================
    def generate_random_particles(self, num=120):
        self.particles = []
        for _ in range(num):
            px = random.uniform(-2.6, 2.6)
            py = random.uniform(-2.6, 2.6)
            self.particles.append((px, py))

    def converge_particles_to_pose(self, x, y, yaw):
        """Simulates AMCL covariance update: collapses particles around pose with Gaussian noise."""
        self.particles = []
        for _ in range(120):
            # Standard deviations: 0.15m for X/Y (matching covariance diagonal)
            px = random.gauss(x, 0.12)
            py = random.gauss(y, 0.12)
            self.particles.append((px, py))
        self.is_localized = True

    # ==========================
    # Action Client Simulation
    # ==========================
    def publish_initial_pose(self):
        """Executes Node 1: Programmatic Initial Pose setting."""
        self.log("==========================================================", "HEADER")
        self.log("[initial_pose.py] Initializing ROS Node 'initial_pose_publisher'...")
        self.log("[initial_pose.py] Broadcasting PoseWithCovarianceStamped to '/initialpose'...")
        self.log(f"[initial_pose.py] Pose: x={self.robot_x:.2f}m, y={self.robot_y:.2f}m, yaw={self.robot_yaw:.2f}rad")
        self.log("[initial_pose.py] Covariance: Var(X)=0.25, Var(Y)=0.25, Var(Yaw)=0.0685 rad^2")

        self.converge_particles_to_pose(self.robot_x, self.robot_y, self.robot_yaw)
        self.status_var.set("AMCL Localized! Initial pose published to /initialpose successfully.")
        self.log("[SUCCESS] AMCL Particle Filter locked! Robot localized on map without RViz GUI intervention.")
        self.log("==========================================================", "HEADER")

    def start_full_mission(self):
        """1-Click button: Publishes initial pose, then starts waypoint mission automatically."""
        self.reset_all()
        self.publish_initial_pose()
        self.root.after(800, self.start_waypoint_nav)

    def start_waypoint_nav(self):
        """Executes Node 2: Multi-Station Warehouse Mission."""
        if not self.is_localized:
            self.log("[WARN] Robot is not yet localized! Auto-triggering initial_pose first...")
            self.publish_initial_pose()

        self.log("==========================================================", "HEADER")
        self.log("[waypoint_navigator.py] Connecting to 'move_base' Action Server...")
        self.log("[waypoint_navigator.py] Action Server Connected! Starting 4-Station Mission.")
        self.log("==========================================================", "HEADER")

        self.current_wp_index = 0
        self.send_current_goal()

    def send_current_goal(self):
        if self.current_wp_index >= len(WAYPOINTS):
            self.finish_mission()
            return

        wp = WAYPOINTS[self.current_wp_index]
        self.is_navigating = True
        self.dwell_timer_active = False

        self.log(f"\n---> [STATION {self.current_wp_index + 1}/4]: Sending MoveBaseGoal '{wp['name']}'", "HEADER")
        self.log(f"     Target Coords: (x: {wp['x']:.2f} m, y: {wp['y']:.2f} m, yaw: {wp['yaw']:.2f} rad)")
        self.log(f"[CALLBACK - ACTIVE] Goal '{wp['name']}' accepted by move_base action server.")
        self.status_var.set(f"Traveling to Station {self.current_wp_index + 1}/4: {wp['name']}...")

    def finish_mission(self):
        self.is_navigating = False
        self.mission_completed = True
        self.status_var.set("Mission Accomplished! All warehouse stations reached successfully.")
        self.log("\n==========================================================", "HEADER")
        self.log("[SUCCESS] Autonomous Warehouse Navigation Mission Completed 100%!", "SUCCESS")
        self.log("==========================================================", "HEADER")

    def reset_all(self):
        self.robot_x = -2.0
        self.robot_y = -0.5
        self.robot_yaw = 0.0
        self.current_wp_index = -1
        self.is_navigating = False
        self.dwell_timer_active = False
        self.mission_completed = False
        self.is_localized = False
        self.path_trail.clear()
        self.generate_random_particles(120)
        self.status_var.set("Status: Reset complete. Ready to run.")
        self.log("[SYSTEM] Simulation reset to initial spawn (-2.0, -0.5).")

    # ==========================
    # Main Simulation Step Loop
    # ==========================
    def simulation_loop(self):
        # Navigation physics & control
        if self.is_navigating and self.current_wp_index < len(WAYPOINTS):
            if self.dwell_timer_active:
                remaining = self.dwell_end_time - time.time()
                if remaining <= 0:
                    self.dwell_timer_active = False
                    self.current_wp_index += 1
                    self.send_current_goal()
                else:
                    self.status_var.set(f"At {WAYPOINTS[self.current_wp_index]['name']} | Dwell Time: {remaining:.1f}s...")
            else:
                self.step_navigation()

        self.render()
        self.root.after(33, self.simulation_loop)

    def step_navigation(self):
        target = WAYPOINTS[self.current_wp_index]
        tx, ty = target["x"], target["y"]
        dx = tx - self.robot_x
        dy = ty - self.robot_y
        dist = math.hypot(dx, dy)

        # Waypoint arrival threshold
        if dist < 0.08:
            # Reached goal!
            self.log(f"[CALLBACK - DONE] Goal '{target['name']}' SUCCEEDED (Status: 3 - GoalStatus.SUCCEEDED)", "SUCCESS")
            self.log(f"[OPERATION] Task: {target['task']}")
            self.log("[OPERATION] Pausing 2.0s for simulated warehouse loading/unloading...")
            self.dwell_timer_active = True
            self.dwell_end_time = time.time() + 2.0
            return

        # Simple Local Obstacle Avoidance + Pure Pursuit
        target_angle = math.atan2(dy, dx)
        
        # Obstacle repulsive potential field
        repulse_vx = 0.0
        repulse_vy = 0.0
        for obs in OBSTACLES:
            ox, oy, r = obs["x"], obs["y"], obs["radius"]
            odist = math.hypot(self.robot_x - ox, self.robot_y - oy)
            safe_dist = r + 0.35
            if odist < safe_dist:
                force = (safe_dist - odist) / safe_dist
                repulse_vx += ((self.robot_x - ox) / odist) * force * 1.5
                repulse_vy += ((self.robot_y - oy) / odist) * force * 1.5

        # Blended heading
        heading_x = math.cos(target_angle) + repulse_vx
        heading_y = math.sin(target_angle) + repulse_vy
        desired_yaw = math.atan2(heading_y, heading_x)

        # Differential drive kinematic update
        yaw_err = (desired_yaw - self.robot_yaw + math.pi) % (2 * math.pi) - math.pi
        self.robot_yaw += yaw_err * 0.15

        speed = min(0.045, dist * 0.2)
        self.robot_x += math.cos(self.robot_yaw) * speed
        self.robot_y += math.sin(self.robot_yaw) * speed

        # Update AMCL particles with motion model
        if self.is_localized:
            new_particles = []
            for px, py in self.particles:
                npx = px + (math.cos(self.robot_yaw) * speed) + random.gauss(0, 0.005)
                npy = py + (math.sin(self.robot_yaw) * speed) + random.gauss(0, 0.005)
                new_particles.append((npx, npy))
            self.particles = new_particles

        # Update trail
        if len(self.path_trail) == 0 or math.hypot(self.robot_x - self.path_trail[-1][0], self.robot_y - self.path_trail[-1][1]) > 0.05:
            self.path_trail.append((self.robot_x, self.robot_y))
            if random.random() < 0.15:
                self.log(f"[CALLBACK - FEEDBACK] En route to '{target['name']}' | Pose: (x={self.robot_x:.2f}, y={self.robot_y:.2f})")

    # ==========================
    # Rendering
    # ==========================
    def render(self):
        self.canvas.delete("all")

        # 1. Draw Grid (0.5m grid lines)
        for gx in range(-3, 4):
            sx1, sy1 = world_to_screen(gx, -3)
            sx2, sy2 = world_to_screen(gx, 3)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill="#1e1e2e", width=1)
        for gy in range(-3, 4):
            sx1, sy1 = world_to_screen(-3, gy)
            sx2, sy2 = world_to_screen(3, gy)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill="#1e1e2e", width=1)

        # 2. Draw Outer Boundary Walls
        bx1, by1 = world_to_screen(-2.7, 2.7)
        bx2, by2 = world_to_screen(2.7, -2.7)
        self.canvas.create_rectangle(bx1, by1, bx2, by2, outline="#45475a", width=3)

        # 3. Draw Warehouse Obstacles
        for obs in OBSTACLES:
            ox, oy, r = obs["x"], obs["y"], obs["radius"]
            osx, osy = world_to_screen(ox, oy)
            sr = r * SCALE
            self.canvas.create_oval(osx - sr, osy - sr, osx + sr, osy + sr,
                                    fill="#f38ba8", outline="#eba0ac", width=2)
            self.canvas.create_text(osx, osy, text=obs["name"], fill="#11111b",
                                    font=("Segoe UI", 7, "bold"))

        # 4. Draw Waypoints
        for idx, wp in enumerate(WAYPOINTS, start=1):
            wsx, wsy = world_to_screen(wp["x"], wp["y"])
            # Waypoint marker ring
            is_active = (self.is_navigating and self.current_wp_index == idx - 1)
            color = "#a6e3a1" if is_active else "#fab387"
            self.canvas.create_oval(wsx - 14, wsy - 14, wsx + 14, wsy + 14,
                                    outline=color, width=2, dash=(4, 2) if not is_active else None)
            self.canvas.create_oval(wsx - 4, wsy - 4, wsx + 4, wsy + 4, fill=color, outline="")
            self.canvas.create_text(wsx, wsy - 20, text=f"{idx}. {wp['name']}",
                                    fill="#cdd6f4", font=("Segoe UI", 8, "bold"))

        # 5. Draw Planned Global Path Line
        if self.is_navigating and self.current_wp_index < len(WAYPOINTS):
            target = WAYPOINTS[self.current_wp_index]
            rsx, rsy = world_to_screen(self.robot_x, self.robot_y)
            tsx, tsy = world_to_screen(target["x"], target["y"])
            self.canvas.create_line(rsx, rsy, tsx, tsy, fill="#94e2d5", width=2, dash=(6, 4))

        # 6. Draw Robot Trajectory Trail
        if len(self.path_trail) > 1:
            points = []
            for tx, ty in self.path_trail[-100:]:
                psx, psy = world_to_screen(tx, ty)
                points.extend([psx, psy])
            self.canvas.create_line(*points, fill="#89dceb", width=2)

        # 7. Draw AMCL Particle Cloud
        for px, py in self.particles:
            psx, psy = world_to_screen(px, py)
            self.canvas.create_oval(psx - 2, psy - 2, psx + 2, psy + 2,
                                    fill="#a6e3a1", outline="")

        # 8. Draw TurtleBot3 Robot (Chassis & Lidar)
        rx, ry = world_to_screen(self.robot_x, self.robot_y)
        rr = self.robot_radius * SCALE

        # Footprint
        self.canvas.create_oval(rx - rr, ry - rr, rx + rr, ry + rr,
                                fill="#89b4fa", outline="#b4befe", width=2)
        # Laser Lidar puck in center
        self.canvas.create_oval(rx - 5, ry - 5, rx + 5, ry + 5,
                                fill="#f38ba8", outline="#11111b")
        # Heading arrow
        hx = rx + math.cos(self.robot_yaw) * (rr + 12)
        hy = ry - math.sin(self.robot_yaw) * (rr + 12)
        self.canvas.create_line(rx, ry, hx, hy, fill="#f9e2af", width=3, arrow=tk.LAST)

        # Robot Tag
        self.canvas.create_text(rx, ry + rr + 12, text="TurtleBot3",
                                fill="#89b4fa", font=("Segoe UI", 8, "bold"))

def main():
    root = tk.Tk()
    app = TurtleBot3SimulatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

