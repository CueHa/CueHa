# visualize.py
# Skeleton visualizer for the 2026 Autonomous Newbie Project.
# This file reads scenarios from scenarios.py and decisions from controller.py,
# then displays them in a simple Tkinter visual interface.

import tkinter as tk
import math

from scenarios import scenarios
from controller import controller


WINDOW_W = 980
WINDOW_H = 640

CANVAS_W = 640
CANVAS_H = 540

ROAD_LEFT = 180
ROAD_RIGHT = 460
ROAD_TOP = 0
ROAD_BOTTOM = 500
ROAD_CENTER_X = (ROAD_LEFT + ROAD_RIGHT) // 2

ROAD_WIDTH_M = 2.0
PIXELS_PER_METER_X = (ROAD_RIGHT - ROAD_LEFT) / ROAD_WIDTH_M

SIDE_ROAD_WIDTH_M = 0.75
SIDE_ROAD_WIDTH_PX = SIDE_ROAD_WIDTH_M * PIXELS_PER_METER_X

MID_SIDE_ROAD_TOP = 210
MID_SIDE_ROAD_BOTTOM = 320
TOP_SIDE_ROAD_BOTTOM = MID_SIDE_ROAD_TOP

VEHICLE_BASE_Y = 420

FRAME_DELAY_MS = 35
MOTION_PIXELS_PER_MPS = 55.0
MAX_ANIMATION_FRAMES = 140

TURN_RATE_LEFT_DEG_PER_S = -35.0
TURN_RATE_RIGHT_DEG_PER_S = 35.0

STOP_DECEL_MPS2 = 4.0
SLOW_APPROACH_MPS2 = 2.0
ACCEL_MPS2 = 2.5

SLOW_TARGET_MPS = 1.5
ACCEL_MIN_TARGET_MPS = 4.5
ACCEL_OFFSET_TARGET_MPS = 1.0


class VisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Autonomous Newbie Project Visualizer")

        self.index = 0
        self.animating = False
        self.after_id = None
        self.frame_i = 0

        self.vehicle_x = ROAD_CENTER_X
        self.vehicle_y = VEHICLE_BASE_Y
        self.vehicle_heading_deg = 0.0
        self.vehicle_speed_mps = 0.0
        self.initial_speed_mps = 0.0

        self.command_steering = "STRAIGHT"
        self.command_speed_action = "SLOW"

        self.title_label = tk.Label(
            root,
            text="Autonomous Newbie Project Visualizer",
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
        self.output_label.pack(anchor="w", pady=(4, 12))

        self.status_title = tk.Label(
            self.info_frame,
            text="Visualizer Status",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.status_title.pack(anchor="w")

        self.status_label = tk.Label(
            self.info_frame,
            text="Ready",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.status_label.pack(anchor="w", pady=(4, 12))

        self.note_label = tk.Label(
            self.info_frame,
            text=(
                "Main road width = 2.0 m.\n"
                "Side roads = 0.75 m each.\n"
                "Top side roads reach the top border.\n"
                "All side roads extend to the canvas edges.\n"
                "Playback follows controller steering and speed_action."
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
            self.controls,
            text="Previous",
            width=12,
            command=self.prev_scenario
        )
        self.prev_button.pack(side="left", padx=6)

        self.play_button = tk.Button(
            self.controls,
            text="Play",
            width=12,
            command=self.play_scenario
        )
        self.play_button.pack(side="left", padx=6)

        self.reset_button = tk.Button(
            self.controls,
            text="Reset",
            width=12,
            command=self.reset_current
        )
        self.reset_button.pack(side="left", padx=6)

        self.next_button = tk.Button(
            self.controls,
            text="Next",
            width=12,
            command=self.next_scenario
        )
        self.next_button.pack(side="left", padx=6)

        self.root.bind("<Left>", lambda event: self.prev_scenario())
        self.root.bind("<Right>", lambda event: self.next_scenario())
        self.root.bind("<space>", lambda event: self.play_scenario())
        self.root.bind("r", lambda event: self.reset_current())

        self.reset_vehicle_state()
        self.refresh_view()

    def current_scenario(self):
        return scenarios[self.index]

    def run_controller_for_current_scenario(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]

        steering, speed_action = controller(
            inputs["obstacle_distance_m"],
            inputs["lane_offset_m"],
            inputs["heading_error_deg"],
            inputs["speed_mps"],
            inputs["e_stop"],
            inputs["left_clear"],
            inputs["right_clear"],
            inputs["sensor_valid"]
        )

        return steering, speed_action

    def lane_offset_to_x(self, lane_offset_m):
        return ROAD_CENTER_X + lane_offset_m * PIXELS_PER_METER_X

    def x_to_lane_offset_m(self, x):
        return (x - ROAD_CENTER_X) / PIXELS_PER_METER_X

    def obstacle_y_from_distance(self, distance_m):
        if distance_m >= 999.0:
            return None

        distance_clamped = max(0.5, min(distance_m, 3.0))

        nearest_y = 360.0
        farthest_y = 140.0

        t = (distance_clamped - 0.5) / (3.0 - 0.5)
        return nearest_y + t * (farthest_y - nearest_y)

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

    def reset_vehicle_state(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]

        self.vehicle_x = self.lane_offset_to_x(inputs["lane_offset_m"])
        self.vehicle_y = VEHICLE_BASE_Y
        self.vehicle_heading_deg = inputs["heading_error_deg"]
        self.vehicle_speed_mps = inputs["speed_mps"]
        self.initial_speed_mps = inputs["speed_mps"]

        self.command_steering, self.command_speed_action = self.run_controller_for_current_scenario()

        self.frame_i = 0

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.animating = False

    def reset_current(self):
        self.reset_vehicle_state()
        self.status_label.config(text="Reset current scenario")
        self.refresh_view()

    def prev_scenario(self):
        if self.animating:
            return

        self.index = (self.index - 1) % len(scenarios)
        self.reset_vehicle_state()
        self.status_label.config(text="Moved to previous scenario")
        self.refresh_view()

    def next_scenario(self):
        if self.animating:
            return

        self.index = (self.index + 1) % len(scenarios)
        self.reset_vehicle_state()
        self.status_label.config(text="Moved to next scenario")
        self.refresh_view()

    def play_scenario(self):
        if self.animating:
            return

        self.reset_vehicle_state()
        self.animating = True
        self.status_label.config(
            text=(
                f"Animating controller output: "
                f"{self.command_steering} + {self.command_speed_action}"
            )
        )
        self.animate_step()

    def apply_controller_speed_action(self, dt):
        if self.command_speed_action == "STOP":
            self.vehicle_speed_mps = max(
                0.0,
                self.vehicle_speed_mps - STOP_DECEL_MPS2 * dt
            )

        elif self.command_speed_action == "SLOW":
            if self.vehicle_speed_mps > SLOW_TARGET_MPS:
                self.vehicle_speed_mps = max(
                    SLOW_TARGET_MPS,
                    self.vehicle_speed_mps - SLOW_APPROACH_MPS2 * dt
                )
            else:
                self.vehicle_speed_mps = min(
                    SLOW_TARGET_MPS,
                    self.vehicle_speed_mps + SLOW_APPROACH_MPS2 * dt
                )

        elif self.command_speed_action == "ACCELERATE":
            accel_target = max(
                ACCEL_MIN_TARGET_MPS,
                self.initial_speed_mps + ACCEL_OFFSET_TARGET_MPS
            )
            self.vehicle_speed_mps = min(
                accel_target,
                self.vehicle_speed_mps + ACCEL_MPS2 * dt
            )

    def apply_controller_steering(self, dt):
        if self.command_steering == "LEFT":
            self.vehicle_heading_deg += TURN_RATE_LEFT_DEG_PER_S * dt

        elif self.command_steering == "RIGHT":
            self.vehicle_heading_deg += TURN_RATE_RIGHT_DEG_PER_S * dt

        if self.vehicle_heading_deg > 90.0:
            self.vehicle_heading_deg = 90.0
        elif self.vehicle_heading_deg < -90.0:
            self.vehicle_heading_deg = -90.0

    def animate_step(self):
        if not self.animating:
            return

        dt = FRAME_DELAY_MS / 1000.0
        self.frame_i += 1

        heading_locked = abs(self.vehicle_heading_deg) >= 90.0

        if not heading_locked:
            self.apply_controller_speed_action(dt)
            self.apply_controller_steering(dt)
        else:
            if self.vehicle_heading_deg > 0:
                self.vehicle_heading_deg = 90.0
            else:
                self.vehicle_heading_deg = -90.0

        distance_px = self.vehicle_speed_mps * MOTION_PIXELS_PER_MPS * dt
        heading_rad = math.radians(self.vehicle_heading_deg)

        dx = math.sin(heading_rad) * distance_px
        dy = -math.cos(heading_rad) * distance_px

        self.vehicle_x += dx
        self.vehicle_y += dy

        self.refresh_view()

        out_of_bounds = (
            self.vehicle_x < -40
            or self.vehicle_x > CANVAS_W + 40
            or self.vehicle_y < -40
            or self.vehicle_y > CANVAS_H + 40
        )

        stopped_from_command = (
            self.command_speed_action == "STOP"
            and self.vehicle_speed_mps <= 0.02
            and self.frame_i > 8
        )

        finished_by_length = self.frame_i >= MAX_ANIMATION_FRAMES

        if out_of_bounds or stopped_from_command or finished_by_length:
            self.animating = False
            self.after_id = None
            self.status_label.config(text="Playback complete")
            return

        self.after_id = self.root.after(FRAME_DELAY_MS, self.animate_step)

    def draw_road_network(self):
        road_fill = "#6f7175"
        road_outline = "black"

        # Main road
        self.canvas.create_rectangle(
            ROAD_LEFT, ROAD_TOP, ROAD_RIGHT, ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        # Top left side road, extended to left edge and top border
        self.canvas.create_rectangle(
            0,
            ROAD_TOP,
            ROAD_LEFT,
            TOP_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        # Top right side road, extended to right edge and top border
        self.canvas.create_rectangle(
            ROAD_RIGHT,
            ROAD_TOP,
            CANVAS_W,
            TOP_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        # Middle left side road, extended to left edge
        self.canvas.create_rectangle(
            0,
            MID_SIDE_ROAD_TOP,
            ROAD_LEFT,
            MID_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        # Middle right side road, extended to right edge
        self.canvas.create_rectangle(
            ROAD_RIGHT,
            MID_SIDE_ROAD_TOP,
            CANVAS_W,
            MID_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        # Main center guide
        self.canvas.create_line(
            ROAD_CENTER_X, ROAD_TOP, ROAD_CENTER_X, ROAD_BOTTOM,
            fill="white",
            dash=(10, 10),
            width=2
        )

        # Bottom position reference
        self.canvas.create_text(
            ROAD_LEFT + 18,
            ROAD_BOTTOM + 18,
            text="-1.0 m",
            font=("Arial", 9)
        )
        self.canvas.create_text(
            ROAD_CENTER_X,
            ROAD_BOTTOM + 18,
            text="0.0 m",
            font=("Arial", 9, "bold")
        )
        self.canvas.create_text(
            ROAD_RIGHT - 18,
            ROAD_BOTTOM + 18,
            text="+1.0 m",
            font=("Arial", 9)
        )

    def refresh_view(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]
        steering, speed_action = self.run_controller_for_current_scenario()

        self.command_steering = steering
        self.command_speed_action = speed_action

        self.scenario_name_label.config(
            text=f"Scenario {self.index + 1}/{len(scenarios)}\n{scenario['name']}"
        )

        input_lines = []
        for key, value in inputs.items():
            input_lines.append(f"{key}: {value}")
        self.inputs_label.config(text="\n".join(input_lines))

        output_text = (
            f"steering:     {steering}\n"
            f"speed_action: {speed_action}"
        )
        self.output_label.config(text=output_text)

        self.draw_scene(inputs, steering, speed_action)

    def draw_scene(self, inputs, steering, speed_action):
        self.canvas.delete("all")

        self.canvas.create_rectangle(
            0, 0, CANVAS_W, CANVAS_H,
            fill="#dceccf",
            outline=""
        )

        self.draw_road_network()

        obstacle_y = self.obstacle_y_from_distance(
            inputs["obstacle_distance_m"])
        if obstacle_y is not None:
            self.canvas.create_rectangle(
                270, obstacle_y - 20, 370, obstacle_y + 20,
                fill="#e2634f",
                outline="black",
                width=2
            )
            self.canvas.create_text(
                320, obstacle_y,
                text=f"OBSTACLE\n{inputs['obstacle_distance_m']:.1f} m",
                font=("Arial", 9, "bold"),
                justify="center"
            )
        else:
            self.canvas.create_text(
                320, 200,
                text="No immediate obstacle",
                font=("Arial", 10, "italic")
            )

        vehicle_shape = [
            (-15, 16),
            (15, 16),
            (0, -22),
        ]

        rotated_vehicle = self.rotated_points(
            self.vehicle_x,
            self.vehicle_y,
            vehicle_shape,
            self.vehicle_heading_deg
        )

        self.canvas.create_polygon(
            rotated_vehicle,
            fill="#87ceeb",
            outline="black",
            width=2
        )

        self.canvas.create_text(
            self.vehicle_x,
            self.vehicle_y + 34,
            text="Vehicle",
            font=("Arial", 10, "bold")
        )

        live_offset_m = self.x_to_lane_offset_m(self.vehicle_x)

        vehicle_state_text = (
            f"heading: {self.vehicle_heading_deg:.1f} deg\n"
            f"offset:  {live_offset_m:.2f} m\n"
            f"speed:   {self.vehicle_speed_mps:.1f} m/s"
        )

        self.canvas.create_text(
            self.vehicle_x,
            self.vehicle_y + 64,
            text=vehicle_state_text,
            font=("Courier New", 9),
            justify="center"
        )

        if speed_action == "STOP":
            banner_fill = "#f4d46c"
        elif speed_action == "SLOW":
            banner_fill = "#eadf98"
        else:
            banner_fill = "#bce6bc"

        self.canvas.create_rectangle(
            180, 510, 460, 535,
            fill=banner_fill,
            outline="black"
        )
        self.canvas.create_text(
            320, 522,
            text=f"Decision: {steering} + {speed_action}",
            font=("Arial", 10, "bold")
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")
    app = VisualizerApp(root)
    root.mainloop()
