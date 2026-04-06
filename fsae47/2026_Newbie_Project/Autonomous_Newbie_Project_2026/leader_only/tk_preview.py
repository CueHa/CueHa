import tkinter as tk
import math

WINDOW_W = 980
WINDOW_H = 640

CANVAS_W = 640
CANVAS_H = 540

FRAME_DELAY_MS = 35
TOTAL_FRAMES = 45

ROAD_LEFT = 140
ROAD_RIGHT = 500
ROAD_TOP = 60
ROAD_BOTTOM = 500
ROAD_CENTER_X = (ROAD_LEFT + ROAD_RIGHT) // 2

LEFT_BOUNDARY = 230
RIGHT_BOUNDARY = 410

SCENARIOS = [
    {
        "name": "Clear Path, Centered",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True,
        },
        "output": {
            "steering": "STRAIGHT",
            "speed_action": "ACCELERATE",
        },
    },
    {
        "name": "Close Obstacle Ahead, No Safe Side",
        "inputs": {
            "obstacle_distance_m": 0.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.5,
            "e_stop": False,
            "left_clear": False,
            "right_clear": False,
            "sensor_valid": True,
        },
        "output": {
            "steering": "STRAIGHT",
            "speed_action": "STOP",
        },
    },
    {
        "name": "Obstacle Ahead, Left Clear",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True,
        },
        "output": {
            "steering": "LEFT",
            "speed_action": "SLOW",
        },
    },
    {
        "name": "Obstacle Ahead, Right Clear",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True,
        },
        "output": {
            "steering": "RIGHT",
            "speed_action": "SLOW",
        },
    },
    {
        "name": "Large Heading Error at Speed",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.1,
            "heading_error_deg": 22.0,
            "speed_mps": 4.5,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True,
        },
        "output": {
            "steering": "LEFT",
            "speed_action": "ACCELERATE",
        },
    },
    {
        "name": "Emergency Stop Active",
        "inputs": {
            "obstacle_distance_m": 2.0,
            "lane_offset_m": -0.4,
            "heading_error_deg": -12.0,
            "speed_mps": 3.0,
            "e_stop": True,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True,
        },
        "output": {
            "steering": "STRAIGHT",
            "speed_action": "STOP",
        },
    },
    {
        "name": "Obstacle Plus Heading Conflict",
        "inputs": {
            "obstacle_distance_m": 1.7,
            "lane_offset_m": -0.2,
            "heading_error_deg": 18.0,
            "speed_mps": 3.5,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True,
        },
        "output": {
            "steering": "RIGHT",
            "speed_action": "SLOW",
        },
    },
    {
        "name": "Mild Drift, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.25,
            "heading_error_deg": 5.0,
            "speed_mps": 2.2,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True,
        },
        "output": {
            "steering": "LEFT",
            "speed_action": "ACCELERATE",
        },
    },
]


class PreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Autonomous Visualizer Preview")
        self.index = 0
        self.animating = False
        self.after_id = None

        self.vehicle_x = 0.0
        self.vehicle_y = 0.0
        self.vehicle_heading_deg = 0.0
        self.vehicle_state = "normal"

        self.frame_i = 0
        self.failure_reason = None
        self.motion_script_name = ""

        self.title_label = tk.Label(
            root,
            text="Autonomous Newbie Project, Shape-Only Visualizer Preview",
            font=("Arial", 16, "bold"),
            pady=8,
        )
        self.title_label.pack()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.canvas = tk.Canvas(
            self.main_frame,
            width=CANVAS_W,
            height=CANVAS_H,
            bg="white",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.canvas.pack(side="left", padx=(0, 14))

        self.info_frame = tk.Frame(self.main_frame, width=300)
        self.info_frame.pack(side="left", fill="y")

        self.scenario_name_label = tk.Label(
            self.info_frame,
            text="",
            font=("Arial", 13, "bold"),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.scenario_name_label.pack(anchor="w", pady=(0, 10))

        self.inputs_title = tk.Label(
            self.info_frame,
            text="Inputs",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.inputs_title.pack(anchor="w")

        self.inputs_label = tk.Label(
            self.info_frame,
            text="",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.inputs_label.pack(anchor="w", pady=(4, 12))

        self.output_title = tk.Label(
            self.info_frame,
            text="Controller Output",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.output_title.pack(anchor="w")

        self.output_label = tk.Label(
            self.info_frame,
            text="",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.output_label.pack(anchor="w", pady=(4, 8))

        self.script_title = tk.Label(
            self.info_frame,
            text="Motion Script",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.script_title.pack(anchor="w")

        self.script_label = tk.Label(
            self.info_frame,
            text="",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.script_label.pack(anchor="w", pady=(4, 12))

        self.note_label = tk.Label(
            self.info_frame,
            text=(
                "Preview only.\n"
                "Fixed playback, no realistic physics.\n"
                "Failure appears if obstacle collision, blocked-side entry,\n"
                "or leaving the allowed area is detected."
            ),
            font=("Arial", 9),
            fg="gray30",
            justify="left",
            wraplength=290,
        )
        self.note_label.pack(anchor="w", pady=(10, 0))

        self.controls = tk.Frame(root)
        self.controls.pack(pady=8)

        self.prev_button = tk.Button(
            self.controls, text="Previous", width=12, command=self.prev_scenario)
        self.prev_button.pack(side="left", padx=6)

        self.play_button = tk.Button(
            self.controls, text="Play", width=12, command=self.play_scenario)
        self.play_button.pack(side="left", padx=6)

        self.reset_button = tk.Button(
            self.controls, text="Reset", width=12, command=self.reset_current)
        self.reset_button.pack(side="left", padx=6)

        self.next_button = tk.Button(
            self.controls, text="Next", width=12, command=self.next_scenario)
        self.next_button.pack(side="left", padx=6)

        self.root.bind("<Left>", lambda event: self.prev_scenario())
        self.root.bind("<Right>", lambda event: self.next_scenario())
        self.root.bind("<space>", lambda event: self.play_scenario())
        self.root.bind("r", lambda event: self.reset_current())

        self.reset_vehicle()
        self.draw_scene()

    def current_scenario(self):
        return SCENARIOS[self.index]

    def lane_offset_to_x(self, lane_offset_m):
        return ROAD_CENTER_X + lane_offset_m * 120.0

    def obstacle_y_from_distance(self, distance_m):
        if distance_m >= 999:
            return None
        distance_clamped = max(0.5, min(distance_m, 3.0))
        return 320 - ((3.0 - distance_clamped) / 2.5) * 180

    def reset_vehicle(self):
        scenario = self.current_scenario()
        lane_offset = scenario["inputs"]["lane_offset_m"]

        self.vehicle_x = self.lane_offset_to_x(lane_offset)
        self.vehicle_y = 420.0
        self.vehicle_heading_deg = 0.0
        self.vehicle_state = "normal"

        self.frame_i = 0
        self.failure_reason = None
        self.motion_script_name = self.describe_script(
            scenario["output"]["steering"],
            scenario["output"]["speed_action"]
        )

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.animating = False

    def reset_current(self):
        self.reset_vehicle()
        self.draw_scene()

    def prev_scenario(self):
        if self.animating:
            return
        self.index = (self.index - 1) % len(SCENARIOS)
        self.reset_vehicle()
        self.draw_scene()

    def next_scenario(self):
        if self.animating:
            return
        self.index = (self.index + 1) % len(SCENARIOS)
        self.reset_vehicle()
        self.draw_scene()

    def play_scenario(self):
        if self.animating:
            return
        self.reset_vehicle()
        self.animating = True
        self.animate_step()

    def describe_script(self, steering, speed_action):
        return f"{steering.lower()} + {speed_action.lower()}"

    def animate_step(self):
        scenario = self.current_scenario()
        steering = scenario["output"]["steering"]
        speed_action = scenario["output"]["speed_action"]

        dx, dy, dtheta = self.get_motion_delta(
            steering, speed_action, self.frame_i)

        self.vehicle_x += dx
        self.vehicle_y += dy
        self.vehicle_heading_deg += dtheta
        self.frame_i += 1

        self.check_failure()

        self.draw_scene()

        if self.failure_reason is not None:
            self.animating = False
            self.after_id = None
            return

        if self.frame_i < TOTAL_FRAMES:
            self.after_id = self.root.after(FRAME_DELAY_MS, self.animate_step)
        else:
            self.animating = False
            self.after_id = None

    def get_motion_delta(self, steering, speed_action, frame_i):
        progress = frame_i / max(1, TOTAL_FRAMES - 1)

        if speed_action == "STOP":
            base_speed = max(0.0, 6.0 * (1.0 - progress))
        elif speed_action == "SLOW":
            base_speed = 3.0
        else:
            base_speed = 6.0

        dy = -base_speed
        dx = 0.0
        dtheta = 0.0

        if steering == "STRAIGHT":
            # Straight with different speed profile only
            return dx, dy, dtheta

        if steering == "LEFT":
            if speed_action == "STOP":
                # Pull over left gently while coming to stop
                dx = -2.8 * (1.0 - 0.5 * progress)
                dy = -max(0.0, 5.0 * (1.0 - progress))
                dtheta = -1.8
            elif speed_action == "SLOW":
                # Normal conservative left turn
                dx = -1.6 - 1.2 * progress
                dy = -3.0
                dtheta = -1.3
            else:
                # Large aggressive left curve
                dx = -2.0 - 2.8 * progress
                dy = -6.0
                dtheta = -2.2

        elif steering == "RIGHT":
            if speed_action == "STOP":
                # Pull over right gently while coming to stop
                dx = 2.8 * (1.0 - 0.5 * progress)
                dy = -max(0.0, 5.0 * (1.0 - progress))
                dtheta = 1.8
            elif speed_action == "SLOW":
                # Normal conservative right turn
                dx = 1.6 + 1.2 * progress
                dy = -3.0
                dtheta = 1.3
            else:
                # Large aggressive right curve
                dx = 2.0 + 2.8 * progress
                dy = -6.0
                dtheta = 2.2

        return dx, dy, dtheta

    def check_failure(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]

        # 1. Leaving allowed area
        if (
            self.vehicle_x < ROAD_LEFT + 10
            or self.vehicle_x > ROAD_RIGHT - 10
            or self.vehicle_y < ROAD_TOP + 10
            or self.vehicle_y > ROAD_BOTTOM - 10
        ):
            self.failure_reason = "Left allowed area"
            self.vehicle_state = "crash_front"
            return

        # 2. Entering blocked side region
        if (not inputs["left_clear"]) and self.vehicle_x < LEFT_BOUNDARY:
            self.failure_reason = "Entered blocked left side"
            self.vehicle_state = "crash_left"
            return

        if (not inputs["right_clear"]) and self.vehicle_x > RIGHT_BOUNDARY:
            self.failure_reason = "Entered blocked right side"
            self.vehicle_state = "crash_right"
            return

        # 3. Obstacle collision
        obstacle_y = self.obstacle_y_from_distance(
            inputs["obstacle_distance_m"])
        if obstacle_y is not None:
            obstacle_left = 265
            obstacle_right = 375
            obstacle_top = obstacle_y - 22
            obstacle_bottom = obstacle_y + 22

            vehicle_half_w = 16
            vehicle_half_h = 16

            if (
                self.vehicle_x + vehicle_half_w >= obstacle_left
                and self.vehicle_x - vehicle_half_w <= obstacle_right
                and self.vehicle_y + vehicle_half_h >= obstacle_top
                and self.vehicle_y - vehicle_half_h <= obstacle_bottom
            ):
                self.failure_reason = "Collided with obstacle"
                self.vehicle_state = "crash_front"
                return

    def draw_scene(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]
        output = scenario["output"]

        self.scenario_name_label.config(
            text=f"Scenario {self.index + 1}/{len(SCENARIOS)}\n{scenario['name']}"
        )

        input_lines = [f"{k}: {v}" for k, v in inputs.items()]
        self.inputs_label.config(text="\n".join(input_lines))

        output_text = (
            f"steering:     {output['steering']}\n"
            f"speed_action: {output['speed_action']}"
        )
        self.output_label.config(text=output_text)
        self.script_label.config(text=self.motion_script_name)

        self.canvas.delete("all")
        self.draw_background(inputs)
        self.draw_obstacle(inputs)
        self.draw_vehicle()
        self.draw_status_banner(output)
        self.draw_failure_overlay()
        self.draw_footer_status()

    def draw_background(self, inputs):
        # Grass / off-road
        self.canvas.create_rectangle(
            0, 0, CANVAS_W, CANVAS_H, fill="#dceccf", outline="")

        # Main road
        self.canvas.create_rectangle(
            ROAD_LEFT, ROAD_TOP, ROAD_RIGHT, ROAD_BOTTOM,
            fill="#6f7175", outline="black", width=2
        )

        # Lane separators
        self.canvas.create_line(ROAD_CENTER_X, ROAD_TOP, ROAD_CENTER_X,
                                ROAD_BOTTOM, fill="white", dash=(10, 10), width=2)
        self.canvas.create_line(
            LEFT_BOUNDARY, ROAD_TOP, LEFT_BOUNDARY, ROAD_BOTTOM, fill="#cfd1d4", dash=(6, 6))
        self.canvas.create_line(
            RIGHT_BOUNDARY, ROAD_TOP, RIGHT_BOUNDARY, ROAD_BOTTOM, fill="#cfd1d4", dash=(6, 6))

        # Path panels near top to reflect background state
        left_fill = "#b8e6b8" if inputs["left_clear"] else "#d9b0b0"
        right_fill = "#b8e6b8" if inputs["right_clear"] else "#d9b0b0"

        self.canvas.create_rectangle(
            155, 80, 225, 130, fill=left_fill, outline="black")
        self.canvas.create_text(
            190, 105,
            text="LEFT\nOPEN" if inputs["left_clear"] else "LEFT\nBLOCKED",
            font=("Arial", 9, "bold")
        )

        self.canvas.create_rectangle(
            415, 80, 485, 130, fill=right_fill, outline="black")
        self.canvas.create_text(
            450, 105,
            text="RIGHT\nOPEN" if inputs["right_clear"] else "RIGHT\nBLOCKED",
            font=("Arial", 9, "bold")
        )

        self.canvas.create_text(
            320, 28, text="Top-down fixed scenario playback", font=("Arial", 11, "bold"))
        self.canvas.create_text(
            190, 150, text="LEFT SIDE", font=("Arial", 9, "bold"))
        self.canvas.create_text(320, 150, text="CENTER",
                                font=("Arial", 9, "bold"))
        self.canvas.create_text(
            450, 150, text="RIGHT SIDE", font=("Arial", 9, "bold"))

    def draw_obstacle(self, inputs):
        obstacle_y = self.obstacle_y_from_distance(
            inputs["obstacle_distance_m"])

        if obstacle_y is None:
            self.canvas.create_text(
                320, 180, text="No immediate obstacle", font=("Arial", 10, "italic"))
            return

        left_clear = inputs["left_clear"]
        right_clear = inputs["right_clear"]

        # Obstacle placement variant
        if not left_clear and right_clear:
            x1, x2 = 250, 370
            label = "OBSTACLE LEFT-BIASED"
        elif left_clear and not right_clear:
            x1, x2 = 270, 390
            label = "OBSTACLE RIGHT-BIASED"
        else:
            x1, x2 = 265, 375
            label = "OBSTACLE STRAIGHT"

        self.canvas.create_rectangle(
            x1, obstacle_y - 22, x2, obstacle_y + 22, fill="#e2634f", outline="black", width=2)
        self.canvas.create_text(
            (x1 + x2) / 2,
            obstacle_y,
            text=label,
            font=("Arial", 9, "bold")
        )

    def rotated_points(self, cx, cy, points, deg):
        rad = math.radians(deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        rotated = []
        for px, py in points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            rotated.extend([cx + rx, cy + ry])
        return rotated

    def draw_vehicle(self):
        x = self.vehicle_x
        y = self.vehicle_y

        if self.vehicle_state == "crash_front":
            points = [(-16, 16), (16, 16), (0, -20)]
            fill = "#ffb3a8"
        elif self.vehicle_state == "crash_left":
            points = [(-20, 10), (8, 16), (2, -20)]
            fill = "#ffb3a8"
        elif self.vehicle_state == "crash_right":
            points = [(-8, 16), (20, 10), (-2, -20)]
            fill = "#ffb3a8"
        else:
            points = [(-15, 16), (15, 16), (0, -22)]
            fill = "#87ceeb"

        rotated = self.rotated_points(x, y, points, self.vehicle_heading_deg)
        self.canvas.create_polygon(
            rotated, fill=fill, outline="black", width=2)

        self.canvas.create_text(x, y + 34, text="Vehicle",
                                font=("Arial", 10, "bold"))

    def draw_status_banner(self, output):
        if self.failure_reason is not None:
            fill = "#f2b0a8"
            text = f"FAILURE: {self.failure_reason}"
        else:
            speed_action = output["speed_action"]
            if speed_action == "STOP":
                fill = "#f4d46c"
            elif speed_action == "SLOW":
                fill = "#eadf98"
            else:
                fill = "#bce6bc"
            text = f"Decision shown: {output['steering']} + {output['speed_action']}"

        self.canvas.create_rectangle(
            180, 512, 460, 536, fill=fill, outline="black")
        self.canvas.create_text(320, 524, text=text,
                                font=("Arial", 10, "bold"))

    def draw_failure_overlay(self):
        if self.failure_reason is None:
            return

        # Static explosion-like burst
        cx = self.vehicle_x
        cy = self.vehicle_y
        r1 = 36
        r2 = 18
        points = []
        for i in range(16):
            angle = (math.pi * 2 * i) / 16.0
            radius = r1 if i % 2 == 0 else r2
            points.extend([cx + math.cos(angle) * radius,
                          cy + math.sin(angle) * radius])

        self.canvas.create_polygon(
            points, fill="#ffb347", outline="#d83a2e", width=3)
        self.canvas.create_text(cx, cy, text="X", font=(
            "Arial", 22, "bold"), fill="#8b0000")

    def draw_footer_status(self):
        if self.animating:
            status = "Animating... Press nothing and let the script play out."
        else:
            status = "Ready. Play with Space or button. Reset with R."
        self.canvas.create_text(320, 490, text=status, font=(
            "Arial", 9, "italic"), fill="gray25")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")
    app = PreviewApp(root)
    root.mainloop()
