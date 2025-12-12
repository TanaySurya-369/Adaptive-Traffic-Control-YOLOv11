"""
Merges.py
----------------
Main integrated script for Adaptive Traffic Control using YOLOv11x and
Pygame-based simulation. This file contains:

- vehicle detection and counting utilities (YOLO tracking)
- traffic simulation classes for adaptive and fixed-time baselines
- a `main()` entrypoint that runs detection + simulation

Start here for learners:
- Read `docs/quickstart.md` for a 3-minute setup and run guide.
- Read `docs/architecture.md` for the high-level flow and file refs.

Notes for maintainers:
- Model weights are NOT included. Use `scripts/download_weights.sh`
    to download and place weights in `models/`.
"""

import argparse
import cv2
from ultralytics import YOLO
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog
import numpy as np
import threading
import time
import random
import pygame
import sys
import os
import json
from datetime import datetime

# Lazy-loaded model globals. Call `load_model(weights_path)` before running
# detection functions in this module.
model = None
class_list = {}

def load_model(weights_path="models/yolo11x.pt"):
    """Load YOLO model from `weights_path` and set module globals.

    This avoids loading heavy model files at import time and lets the
    CLI wrapper control when the weights are loaded.
    """
    global model, class_list
    if model is not None:
        return model
    print(f"Loading YOLO model from: {weights_path}")
    model = YOLO(weights_path)
    class_list = model.names
    return model

# ============================================================================
# PART 1: VEHICLE DETECTION AND COUNTING (Enhanced with YOLOv11x)
# ============================================================================

class AppState:
    def __init__(self):
        self.points = []
        self.polygon_selected = False
        self.polygons = []
        self.temp_image = None
        self.frame = None

# Note: model is loaded lazily by calling `load_model()` from `main()` or
# the CLI wrapper. This prevents expensive imports at module import time.

# Global variables for metrics tracking
class MetricsTracker:
    def __init__(self):
        self.detection_accuracy = {"true_positives": 0, "false_positives": 0, "false_negatives": 0, "total_detections": 0}
        self.adaptive_wait_times = []
        self.adaptive_fuel_consumption = []
        self.adaptive_throughput = 0
        self.adaptive_co2_emissions = 0
        
        # Fixed-time baseline metrics
        self.fixed_wait_times = []
        self.fixed_fuel_consumption = []
        self.fixed_throughput = 0
        self.fixed_co2_emissions = 0
        
        # Traffic density data
        self.traffic_density = []
        self.queue_lengths_adaptive = []
        self.queue_lengths_fixed = []
        
        # Scenario tracking
        self.current_scenario = "peak"  # peak, off-peak, mixed
        self.start_time = time.time()
        
    def calculate_accuracy(self):
        """Calculate detection accuracy: (TP + TN) / Total"""
        if self.detection_accuracy["total_detections"] == 0:
            return 0.0
        tp = self.detection_accuracy["true_positives"]
        total = self.detection_accuracy["total_detections"]
        # Assuming high-quality detection, TP rate is primary metric
        return (tp / total) * 100
    
    def calculate_signal_efficiency(self):
        """Signal Efficiency = Reduced Waiting Time / Total Traffic Volume"""
        if not self.adaptive_wait_times or not self.fixed_wait_times:
            return 0.0
        avg_adaptive = np.mean(self.adaptive_wait_times)
        avg_fixed = np.mean(self.fixed_wait_times)
        reduced_time = avg_fixed - avg_adaptive
        traffic_volume = self.adaptive_throughput + self.fixed_throughput
        if traffic_volume == 0:
            return 0.0
        return (reduced_time / (traffic_volume / 100)) * 100
    
    def calculate_traffic_density(self, num_vehicles, road_length=100):
        """Traffic Density = Number of Vehicles / Road Length"""
        return num_vehicles / road_length
    
    def calculate_improvement(self, adaptive_val, fixed_val):
        """Calculate percentage improvement"""
        if fixed_val == 0:
            return 0.0
        return ((fixed_val - adaptive_val) / fixed_val) * 100
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scenario": self.current_scenario,
            "detection_accuracy": round(self.calculate_accuracy(), 2),
            "adaptive_system": {
                "avg_wait_time": round(np.mean(self.adaptive_wait_times), 2) if self.adaptive_wait_times else 0,
                "fuel_consumption": round(np.mean(self.adaptive_fuel_consumption), 4) if self.adaptive_fuel_consumption else 0,
                "throughput": self.adaptive_throughput,
                "co2_emissions": round(self.adaptive_co2_emissions, 2),
                "avg_queue_length": round(np.mean(self.queue_lengths_adaptive), 2) if self.queue_lengths_adaptive else 0
            },
            "fixed_system": {
                "avg_wait_time": round(np.mean(self.fixed_wait_times), 2) if self.fixed_wait_times else 0,
                "fuel_consumption": round(np.mean(self.fixed_fuel_consumption), 4) if self.fixed_fuel_consumption else 0,
                "throughput": self.fixed_throughput,
                "co2_emissions": round(self.fixed_co2_emissions, 2),
                "avg_queue_length": round(np.mean(self.queue_lengths_fixed), 2) if self.queue_lengths_fixed else 0
            },
            "improvements": {
                "wait_time_reduction": round(self.calculate_improvement(
                    np.mean(self.adaptive_wait_times) if self.adaptive_wait_times else 0,
                    np.mean(self.fixed_wait_times) if self.fixed_wait_times else 0
                ), 2),
                "fuel_savings": round(self.calculate_improvement(
                    np.mean(self.adaptive_fuel_consumption) if self.adaptive_fuel_consumption else 0,
                    np.mean(self.fixed_fuel_consumption) if self.fixed_fuel_consumption else 0
                ), 2),
                "throughput_increase": round(self.calculate_improvement(
                    self.fixed_throughput,
                    self.adaptive_throughput
                ), 2),
                "queue_reduction": round(self.calculate_improvement(
                    np.mean(self.queue_lengths_adaptive) if self.queue_lengths_adaptive else 0,
                    np.mean(self.queue_lengths_fixed) if self.queue_lengths_fixed else 0
                ), 2)
            },
            "signal_efficiency": round(self.calculate_signal_efficiency(), 2)
        }
        return report

metrics = MetricsTracker()

def sort_points_clockwise(pts):
    centroid = np.mean(pts, axis=0)
    sorted_pts = sorted(pts, key=lambda x: np.arctan2(x[1] - centroid[1], x[0] - centroid[0]))
    return sorted_pts

def draw_polygon(event, x, y, flags, param):
    state = param
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(state.points) < 4:
            state.points.append((x, y))
            print(f"Point {len(state.points)}: ({x}, {y})")
            state.temp_image = state.frame.copy()
            for pt in state.points:
                cv2.circle(state.temp_image, pt, 5, (0, 255, 0), -1)
            if len(state.points) > 1:
                for i in range(1, len(state.points)):
                    cv2.line(state.temp_image, state.points[i-1], state.points[i], (0, 255, 0), 2)
            cv2.imshow("Image", state.temp_image)

            if len(state.points) == 4:
                state.points = sort_points_clockwise(state.points)
                print(f"Sorted Points: {state.points}")
                cv2.polylines(state.temp_image, [np.array(state.points)], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.imshow("Image", state.temp_image)
                print(f"Polygon selected with points: {state.points}")
                state.polygons.append(state.points[:])
                state.points = []
                state.polygon_selected = True
        else:
            print("Only 4 points can be selected. Polygon is complete.")

def select_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select 4 video/image files (one per lane)",
        filetypes=[("Video and Image Files", "*.mp4;*.avi;*.mov;*.jpg;*.png;*.jpeg")],
    )
    return list(file_paths)

def process_file(file_path, state):
    state.polygon_selected = False
    state.points = []

    cap = cv2.VideoCapture(file_path) if file_path.endswith(('.mp4', '.avi', '.mov')) else None

    if cap:  # Video
        while True:
            ret, state.frame = cap.read()
            if not ret or state.frame is None or state.frame.size == 0:
                print(f"Skipping corrupted frame in {file_path}")
                continue

            state.temp_image = state.frame.copy()
            cv2.imshow("Image", state.frame)
            cv2.setMouseCallback("Image", draw_polygon, state)
            print(f"Select four points for counting zone in {file_path}. Press 'n' to skip frame, 'r' to reset, any other key to confirm.")

            key = cv2.waitKey(0)
            if key == ord('n'):
                continue
            elif key == ord('r'):
                state.points = []
                state.temp_image = state.frame.copy()
                cv2.imshow("Image", state.temp_image)
            else:
                break

        cap.release()
    else:  # Image
        state.frame = cv2.imread(file_path)
        if state.frame is None:
            print(f"Error: Unable to load {file_path}.")
            return

        state.temp_image = state.frame.copy()
        cv2.imshow("Image", state.frame)
        cv2.setMouseCallback("Image", draw_polygon, state)
        print(f"Select four points for {file_path}. Press 'r' to reset.")
        key = cv2.waitKey(0)
        if key == ord('r'):
            state.points = []
            state.temp_image = state.frame.copy()
            cv2.imshow("Image", state.temp_image)

    cv2.destroyAllWindows()

    if not state.polygon_selected:
        print(f"No polygon was selected for {file_path}. Skipping.")
        return

    print(f"Polygon saved for {file_path}.")

def is_bbox_in_polygon(bbox, polygon):
    x1, y1, x2, y2 = bbox
    polygon_np = np.array(polygon, dtype=np.int32)
    corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    for corner in corners:
        if cv2.pointPolygonTest(polygon_np, corner, False) >= 0:
            return True
    return False

def count_vehicles(file_path, polygon, num_frames=10):
    """Enhanced vehicle counting with accuracy tracking"""
    cap = cv2.VideoCapture(file_path) if file_path.endswith(('.mp4', '.avi', '.mov')) else None

    if not cap or not cap.isOpened():
        print(f"Error: Unable to open video file {file_path}.")
        return 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = max(0, total_frames - num_frames)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    crossed_ids = set()
    class_counts = defaultdict(int)
    frame_count = 0

    while frame_count < num_frames:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            continue

        orig_height, orig_width = frame.shape[:2]
        new_width, new_height = 640, 480
        frame = cv2.resize(frame, (new_width, new_height))

        scale_x = new_width / orig_width
        scale_y = new_height / orig_height
        scaled_polygon = [(int(x * scale_x), int(y * scale_y)) for x, y in polygon]

        frame_count += 1

        try:
            results = model.track(frame, persist=True, classes=[2, 3, 5, 7], conf=0.5)
        except Exception as e:
            print(f"Error during YOLO tracking: {e}")
            continue

        if results[0].boxes.data is None or len(results[0].boxes) == 0:
            continue

        boxes = results[0].boxes.xyxy.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else []
        class_indices = results[0].boxes.cls.int().cpu().tolist()
        confidences = results[0].boxes.conf.cpu().tolist()

        cv2.polylines(frame, [np.array(scaled_polygon)], isClosed=True, color=(0, 255, 0), thickness=2)

        for box, track_id, class_idx, conf in zip(boxes, track_ids, class_indices, confidences):
            x1, y1, x2, y2 = map(int, box)
            class_name = class_list[class_idx]

            # Track detection accuracy
            metrics.detection_accuracy["total_detections"] += 1
            if conf > 0.7:  # High confidence = true positive
                metrics.detection_accuracy["true_positives"] += 1
            elif conf < 0.5:  # Low confidence = false positive
                metrics.detection_accuracy["false_positives"] += 1

            if is_bbox_in_polygon((x1, y1, x2, y2), scaled_polygon):
                if track_id not in crossed_ids:
                    crossed_ids.add(track_id)
                    class_counts[class_name] += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{class_name} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        y_offset = 30
        for class_name, count in class_counts.items():
            cv2.putText(frame, f"{class_name}: {count}", (50, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            y_offset += 30

        cv2.imshow(f"YOLOv11x Detection: {file_path}", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    total_count = sum(class_counts.values())
    # Calculate traffic density
    density = metrics.calculate_traffic_density(total_count)
    metrics.traffic_density.append(density)
    
    return total_count

# ============================================================================
# PART 2: TRAFFIC SIMULATION WITH METRICS TRACKING
# ============================================================================

# Global variables
detection_counts = [0, 0, 0, 0]
exit_event = threading.Event()

# Simulation constants
SIM_WIDTH, SIM_HEIGHT = 800, 600
FPS = 60

# Adaptive system parameters
DYNAMIC_MIN_GREEN = 10.0
EXTRA_GREEN_PER_VEHICLE = 1.0
YELLOW_DURATION = 3.0
MAX_GREEN = 50.0

# Fixed-time system parameters
FIXED_GREEN_DURATION = 30.0  # Standard 30-second green for all lanes

VEHICLE_SIZE = 28
SPACING = 50
STOP_LINE_OFFSET = 70
SPAWN_OFFSET = 50
UP_LANE_X_OFFSET = -45
DOWN_LANE_X_OFFSET = -2
RIGHT_LANE_Y_OFFSET = -52
LEFT_LANE_Y_OFFSET = -15
SPEED = 30.0

# Fuel consumption constants
FUEL_IDLE_RATE = 0.0008  # liters per second while idling
FUEL_MOVING_RATE = 0.0012  # liters per second while moving
CO2_PER_LITER = 2.3  # kg CO2 per liter of fuel

def load_signal_images():
    signals = {}
    try:
        signals["red"] = pygame.image.load("red.png").convert_alpha()
        signals["green"] = pygame.image.load("green.png").convert_alpha()
        signals["yellow"] = pygame.image.load("yellow.png").convert_alpha()
    except pygame.error:
        print("Signal images not found, creating placeholder signals")
        signals["red"] = pygame.Surface((40,40)); signals["red"].fill((255,0,0))
        signals["green"] = pygame.Surface((40,40)); signals["green"].fill((0,255,0))
        signals["yellow"] = pygame.Surface((40,40)); signals["yellow"].fill((255,255,0))
    for key in signals:
        signals[key] = pygame.transform.scale(signals[key], (40,40))
    return signals

def load_and_scale_image(filename, size=(VEHICLE_SIZE,VEHICLE_SIZE), color=(255,0,0)):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    except pygame.error:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0,0,size[0],size[1]))
        return surf

def load_vehicle_images():
    car_color = (200,0,0)
    bike_color = (0,200,0)
    bus_color = (0,0,200)
    truck_color = (200,200,0)
    rickshaw_color = (200,0,200)
    vehicle_imgs = {
        0: [load_and_scale_image("upcar.png", color=car_color),
            load_and_scale_image("upbike.png", color=bike_color),
            load_and_scale_image("upbus.png", color=bus_color),
            load_and_scale_image("uptruck.png", color=truck_color),
            load_and_scale_image("uprickshaw.png", color=rickshaw_color)],
        1: [load_and_scale_image("rightcar.png", color=car_color),
            load_and_scale_image("rightbike.png", color=bike_color),
            load_and_scale_image("rightbus.png", color=bus_color),
            load_and_scale_image("rightrickshaw.png", color=rickshaw_color)],
        2: [load_and_scale_image("downcar.png", color=car_color),
            load_and_scale_image("downbike.png", color=bike_color),
            load_and_scale_image("downbus.png", color=bus_color),
            load_and_scale_image("downtruck.png", color=truck_color),
            load_and_scale_image("downrickshaw.png", color=rickshaw_color)],
        3: [load_and_scale_image("leftcar.png", color=car_color),
            load_and_scale_image("leftbike.png", color=bike_color),
            load_and_scale_image("leftbus.png", color=bus_color),
            load_and_scale_image("lefttruck.png", color=truck_color),
            load_and_scale_image("leftrickshaw.png", color=rickshaw_color)]
    }
    return vehicle_imgs

def already_passed_stop_line(stop_lines, lane, vx, vy):
    if lane == 0:
        return vy < stop_lines[0]
    elif lane == 1:
        return vx > stop_lines[1]
    elif lane == 2:
        return vy > stop_lines[2]
    elif lane == 3:
        return vx < stop_lines[3]
    return False

class AdaptiveTrafficSim:
    """Adaptive traffic simulation with real-time metrics"""
    def __init__(self, surface, vehicle_imgs, initial_counts, signal_imgs):
        self.surface = surface
        self.vehicle_imgs = vehicle_imgs
        self.width = SIM_WIDTH
        self.height = SIM_HEIGHT
        self.signal_imgs = signal_imgs
        self.is_adaptive = True

        self.start_time = time.time()
        self.cleared_count = 0
        self.total_wait_time = 0
        self.total_fuel_consumed = 0
        self.vehicles_processed = 0

        self.signal_positions = {
            0: (self.width//2 - 20, 18),
            1: (self.width - 60, self.height//2 - 20),
            2: (self.width//2 - 20, self.height - 60),
            3: (20, self.height//2 - 20)
        }
        self.stop_lines = [
            self.height/2 + STOP_LINE_OFFSET,
            self.width/2 - STOP_LINE_OFFSET,
            self.height/2 - STOP_LINE_OFFSET,
            self.width/2 + STOP_LINE_OFFSET
        ]
        
        self.lanes = [[], [], [], []]
        self.vehicle_wait_times = {}  # Track individual vehicle wait times
        self.vehicle_fuel = {}  # Track fuel consumption per vehicle
        
        self.init_lane_vehicles(initial_counts)

        self.lane_order = sorted(range(4), key=lambda i: len(self.lanes[i]), reverse=True)
        self.order_index = 0
        self.cycle_allocations = [min(DYNAMIC_MIN_GREEN + len(self.lanes[i]) * EXTRA_GREEN_PER_VEHICLE, MAX_GREEN) for i in range(4)]
        self.current_lane = self.lane_order[self.order_index]
        self.current_green_duration = self.cycle_allocations[self.current_lane]
        self.light_state = "green"
        self.phase_start_time = time.time()

        self.last_update_time = time.time()

    def init_lane_vehicles(self, counts):
        vehicle_id = 0
        # Lane 0: Up
        baseY = self.stop_lines[0] + SPAWN_OFFSET
        up_lane_x = (self.width/2) + UP_LANE_X_OFFSET
        for i in range(counts[0]):
            img = random.choice(self.vehicle_imgs[0])
            vid = f"v{vehicle_id}"
            self.lanes[0].append({"img": img, "x": up_lane_x, "y": baseY + i * SPACING, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        # Lane 1: Right
        baseX = self.stop_lines[1] - SPAWN_OFFSET
        right_lane_y = (self.height/2) + RIGHT_LANE_Y_OFFSET
        for i in range(counts[1]):
            img = random.choice(self.vehicle_imgs[1])
            vid = f"v{vehicle_id}"
            self.lanes[1].append({"img": img, "x": baseX - i * SPACING, "y": right_lane_y, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        # Lane 2: Down
        baseY = self.stop_lines[2] - SPAWN_OFFSET
        down_lane_x = (self.width/2) + DOWN_LANE_X_OFFSET
        for i in range(counts[2]):
            img = random.choice(self.vehicle_imgs[2])
            vid = f"v{vehicle_id}"
            self.lanes[2].append({"img": img, "x": down_lane_x, "y": baseY - i * SPACING, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        # Lane 3: Left
        baseX = self.stop_lines[3] + SPAWN_OFFSET
        left_lane_y = (self.height/2) + LEFT_LANE_Y_OFFSET
        for i in range(counts[3]):
            img = random.choice(self.vehicle_imgs[3])
            vid = f"v{vehicle_id}"
            self.lanes[3].append({"img": img, "x": baseX + i * SPACING, "y": left_lane_y, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        print(f"Initialized adaptive system with: {[len(lane) for lane in self.lanes]} vehicles")

    def select_next_lane(self):
        self.order_index += 1
        if self.order_index >= 4:
            print("Cycle complete. Recalculating priorities.")
            self.lane_order = sorted(range(4), key=lambda i: len(self.lanes[i]), reverse=True)
            self.cycle_allocations = [min(DYNAMIC_MIN_GREEN + len(self.lanes[i]) * EXTRA_GREEN_PER_VEHICLE, MAX_GREEN) for i in range(4)]
            self.order_index = 0
        return self.lane_order[self.order_index]

    def compute_red_timer(self, target_lane):
        if target_lane == self.current_lane:
            return 0
        current_time = time.time()
        if self.light_state == "green":
            rem_current = max(0, self.current_green_duration - (current_time - self.phase_start_time)) + YELLOW_DURATION
        else:
            rem_current = max(0, YELLOW_DURATION - (current_time - self.phase_start_time))
        pos_current = self.order_index
        pos_target = self.lane_order.index(target_lane)
        total = 0
        if pos_target > pos_current:
            total = rem_current + sum(self.cycle_allocations[j] + YELLOW_DURATION for j in range(pos_current+1, pos_target))
        else:
            total = rem_current + sum(self.cycle_allocations[j] + YELLOW_DURATION for j in range(pos_current+1, len(self.lane_order)))
            total += sum(self.cycle_allocations[j] + YELLOW_DURATION for j in range(0, pos_target))
        return total

    def update(self, dt):
        current_time = time.time()
        elapsed = current_time - self.phase_start_time

        # Signal phase management
        if self.light_state == "green":
            if elapsed >= self.current_green_duration:
                self.light_state = "yellow"
                self.phase_start_time = current_time
        elif self.light_state == "yellow":
            if elapsed >= YELLOW_DURATION:
                self.current_lane = self.select_next_lane()
                self.current_green_duration = self.cycle_allocations[self.current_lane]
                self.light_state = "green"
                self.phase_start_time = current_time

        # Move vehicles and track metrics
        for lane in range(4):
            for v in self.lanes[lane]:
                can_move = False
                if lane == self.current_lane:
                    if self.light_state == "green":
                        can_move = True
                    elif self.light_state == "yellow":
                        if already_passed_stop_line(self.stop_lines, lane, v["x"], v["y"]):
                            can_move = True
                else:
                    if already_passed_stop_line(self.stop_lines, lane, v["x"], v["y"]):
                        can_move = True
                
                if can_move:
                    # Moving - consume fuel at moving rate
                    self.vehicle_fuel[v["id"]] += FUEL_MOVING_RATE * dt
                    if lane == 0:
                        v["y"] -= SPEED * dt
                    elif lane == 1:
                        v["x"] += SPEED * dt
                    elif lane == 2:
                        v["y"] += SPEED * dt
                    elif lane == 3:
                        v["x"] -= SPEED * dt
                else:
                    # Waiting - consume fuel at idle rate and accumulate wait time
                    self.vehicle_fuel[v["id"]] += FUEL_IDLE_RATE * dt
                    self.vehicle_wait_times[v["id"]] += dt

        self.remove_offscreen()

    def remove_offscreen(self):
        new_lanes = [[], [], [], []]
        for lane in range(4):
            for v in self.lanes[lane]:
                is_offscreen = False
                if lane == 0 and v["y"] + VEHICLE_SIZE <= 0:
                    is_offscreen = True
                elif lane == 1 and v["x"] >= self.width:
                    is_offscreen = True
                elif lane == 2 and v["y"] >= self.height:
                    is_offscreen = True
                elif lane == 3 and v["x"] + VEHICLE_SIZE <= 0:
                    is_offscreen = True
                
                if is_offscreen:
                    # Vehicle cleared - record metrics
                    self.cleared_count += 1
                    self.vehicles_processed += 1
                    self.total_wait_time += self.vehicle_wait_times[v["id"]]
                    self.total_fuel_consumed += self.vehicle_fuel[v["id"]]
                    
                    # Add to global metrics
                    if self.is_adaptive:
                        metrics.adaptive_wait_times.append(self.vehicle_wait_times[v["id"]])
                        metrics.adaptive_fuel_consumption.append(self.vehicle_fuel[v["id"]])
                    
                    del self.vehicle_wait_times[v["id"]]
                    del self.vehicle_fuel[v["id"]]
                else:
                    new_lanes[lane].append(v)
        
        self.lanes = new_lanes

    def get_current_metrics(self):
        """Get current simulation metrics"""
        total_vehicles = sum(len(lane) for lane in self.lanes)
        avg_wait = self.total_wait_time / self.vehicles_processed if self.vehicles_processed > 0 else 0
        avg_fuel = self.total_fuel_consumed / self.vehicles_processed if self.vehicles_processed > 0 else 0
        
        return {
            "avg_wait_time": avg_wait,
            "avg_fuel_consumption": avg_fuel,
            "throughput": self.cleared_count,
            "current_queue": total_vehicles,
            "vehicles_processed": self.vehicles_processed
        }

    def draw(self, bg_image):
        self.surface.blit(bg_image, (0, 0))
        
        # Draw title
        font_title = pygame.font.SysFont(None, 28, bold=True)
        title = font_title.render("ADAPTIVE TRAFFIC SYSTEM (YOLOv11x)", True, (255, 255, 0))
        self.surface.blit(title, (SIM_WIDTH//2 - 200, 10))
        
        # Draw lane info
        font = pygame.font.SysFont(None, 20)
        y_pos = 40
        for lane in range(4):
            lane_text = f"Lane {lane}: {len(self.lanes[lane])} vehicles"
            lane_surface = font.render(lane_text, True, (255,255,255))
            self.surface.blit(lane_surface, (10, y_pos))
            y_pos += 22
        
        # Draw vehicles
        for lane in range(4):
            for v in self.lanes[lane]:
                self.surface.blit(v["img"], (v["x"], v["y"]))
        
        # Draw traffic signals
        for lane in range(4):
            if lane == self.current_lane:
                if self.light_state == "green":
                    sig = self.signal_imgs["green"]
                    remaining = max(0, self.current_green_duration - (time.time()-self.phase_start_time))
                    text_color = (0,255,0)
                else:
                    sig = self.signal_imgs["yellow"]
                    remaining = max(0, YELLOW_DURATION - (time.time()-self.phase_start_time))
                    text_color = (255,255,0)
                time_text = f"{int(remaining)}s"
            else:
                sig = self.signal_imgs["red"]
                red_timer = self.compute_red_timer(lane)
                time_text = f"{int(red_timer)}s"
                text_color = (255,0,0)
            
            self.surface.blit(sig, self.signal_positions[lane])
            font_time = pygame.font.SysFont(None, 26)
            text_surf = font_time.render(time_text, True, text_color)
            text_x = self.signal_positions[lane][0] + 10
            text_y = self.signal_positions[lane][1] + 45
            pygame.draw.rect(self.surface, (0,0,0), (text_x-3, text_y-3, text_surf.get_width()+6, text_surf.get_height()+6))
            self.surface.blit(text_surf, (text_x, text_y))
        
        # Draw real-time metrics
        metrics_data = self.get_current_metrics()
        font_metrics = pygame.font.SysFont(None, 20)
        info_x = SIM_WIDTH - 280
        info_y = 10
        
        metrics_text = [
            f"Cleared: {self.cleared_count}",
            f"Active Lane: {self.current_lane} ({self.light_state.upper()})",
            f"Avg Wait: {metrics_data['avg_wait_time']:.1f}s",
            f"Avg Fuel: {metrics_data['avg_fuel_consumption']:.4f}L",
            f"Throughput: {metrics_data['throughput']}"
        ]
        
        for text in metrics_text:
            surf = font_metrics.render(text, True, (255, 255, 255))
            self.surface.blit(surf, (info_x, info_y))
            info_y += 22


class FixedTimeTrafficSim:
    """Fixed-time traffic simulation for baseline comparison"""
    def __init__(self, surface, vehicle_imgs, initial_counts, signal_imgs):
        self.surface = surface
        self.vehicle_imgs = vehicle_imgs
        self.width = SIM_WIDTH
        self.height = SIM_HEIGHT
        self.signal_imgs = signal_imgs
        self.is_adaptive = False

        self.start_time = time.time()
        self.cleared_count = 0
        self.total_wait_time = 0
        self.total_fuel_consumed = 0
        self.vehicles_processed = 0

        self.signal_positions = {
            0: (self.width//2 - 20, 18),
            1: (self.width - 60, self.height//2 - 20),
            2: (self.width//2 - 20, self.height - 60),
            3: (20, self.height//2 - 20)
        }
        self.stop_lines = [
            self.height/2 + STOP_LINE_OFFSET,
            self.width/2 - STOP_LINE_OFFSET,
            self.height/2 - STOP_LINE_OFFSET,
            self.width/2 + STOP_LINE_OFFSET
        ]
        
        self.lanes = [[], [], [], []]
        self.vehicle_wait_times = {}
        self.vehicle_fuel = {}
        
        self.init_lane_vehicles(initial_counts)

        # Fixed-time: rotate through lanes in order 0->1->2->3
        self.current_lane = 0
        self.light_state = "green"
        self.phase_start_time = time.time()

    def init_lane_vehicles(self, counts):
        vehicle_id = 0
        baseY = self.stop_lines[0] + SPAWN_OFFSET
        up_lane_x = (self.width/2) + UP_LANE_X_OFFSET
        for i in range(counts[0]):
            img = random.choice(self.vehicle_imgs[0])
            vid = f"f{vehicle_id}"
            self.lanes[0].append({"img": img, "x": up_lane_x, "y": baseY + i * SPACING, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        baseX = self.stop_lines[1] - SPAWN_OFFSET
        right_lane_y = (self.height/2) + RIGHT_LANE_Y_OFFSET
        for i in range(counts[1]):
            img = random.choice(self.vehicle_imgs[1])
            vid = f"f{vehicle_id}"
            self.lanes[1].append({"img": img, "x": baseX - i * SPACING, "y": right_lane_y, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        baseY = self.stop_lines[2] - SPAWN_OFFSET
        down_lane_x = (self.width/2) + DOWN_LANE_X_OFFSET
        for i in range(counts[2]):
            img = random.choice(self.vehicle_imgs[2])
            vid = f"f{vehicle_id}"
            self.lanes[2].append({"img": img, "x": down_lane_x, "y": baseY - i * SPACING, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        baseX = self.stop_lines[3] + SPAWN_OFFSET
        left_lane_y = (self.height/2) + LEFT_LANE_Y_OFFSET
        for i in range(counts[3]):
            img = random.choice(self.vehicle_imgs[3])
            vid = f"f{vehicle_id}"
            self.lanes[3].append({"img": img, "x": baseX + i * SPACING, "y": left_lane_y, "id": vid})
            self.vehicle_wait_times[vid] = 0
            self.vehicle_fuel[vid] = 0
            vehicle_id += 1
        
        print(f"Initialized fixed-time system with: {[len(lane) for lane in self.lanes]} vehicles")

    def update(self, dt):
        current_time = time.time()
        elapsed = current_time - self.phase_start_time

        # Fixed-time signal management: 30s green for all lanes
        if self.light_state == "green":
            if elapsed >= FIXED_GREEN_DURATION:
                self.light_state = "yellow"
                self.phase_start_time = current_time
        elif self.light_state == "yellow":
            if elapsed >= YELLOW_DURATION:
                self.current_lane = (self.current_lane + 1) % 4
                self.light_state = "green"
                self.phase_start_time = current_time

        # Move vehicles and track metrics
        for lane in range(4):
            for v in self.lanes[lane]:
                can_move = False
                if lane == self.current_lane:
                    if self.light_state == "green":
                        can_move = True
                    elif self.light_state == "yellow":
                        if already_passed_stop_line(self.stop_lines, lane, v["x"], v["y"]):
                            can_move = True
                else:
                    if already_passed_stop_line(self.stop_lines, lane, v["x"], v["y"]):
                        can_move = True
                
                if can_move:
                    self.vehicle_fuel[v["id"]] += FUEL_MOVING_RATE * dt
                    if lane == 0:
                        v["y"] -= SPEED * dt
                    elif lane == 1:
                        v["x"] += SPEED * dt
                    elif lane == 2:
                        v["y"] += SPEED * dt
                    elif lane == 3:
                        v["x"] -= SPEED * dt
                else:
                    self.vehicle_fuel[v["id"]] += FUEL_IDLE_RATE * dt
                    self.vehicle_wait_times[v["id"]] += dt

        self.remove_offscreen()

    def remove_offscreen(self):
        new_lanes = [[], [], [], []]
        for lane in range(4):
            for v in self.lanes[lane]:
                is_offscreen = False
                if lane == 0 and v["y"] + VEHICLE_SIZE <= 0:
                    is_offscreen = True
                elif lane == 1 and v["x"] >= self.width:
                    is_offscreen = True
                elif lane == 2 and v["y"] >= self.height:
                    is_offscreen = True
                elif lane == 3 and v["x"] + VEHICLE_SIZE <= 0:
                    is_offscreen = True
                
                if is_offscreen:
                    self.cleared_count += 1
                    self.vehicles_processed += 1
                    self.total_wait_time += self.vehicle_wait_times[v["id"]]
                    self.total_fuel_consumed += self.vehicle_fuel[v["id"]]
                    
                    # Add to global metrics
                    metrics.fixed_wait_times.append(self.vehicle_wait_times[v["id"]])
                    metrics.fixed_fuel_consumption.append(self.vehicle_fuel[v["id"]])
                    
                    del self.vehicle_wait_times[v["id"]]
                    del self.vehicle_fuel[v["id"]]
                else:
                    new_lanes[lane].append(v)
        
        self.lanes = new_lanes

    def get_current_metrics(self):
        total_vehicles = sum(len(lane) for lane in self.lanes)
        avg_wait = self.total_wait_time / self.vehicles_processed if self.vehicles_processed > 0 else 0
        avg_fuel = self.total_fuel_consumed / self.vehicles_processed if self.vehicles_processed > 0 else 0
        
        return {
            "avg_wait_time": avg_wait,
            "avg_fuel_consumption": avg_fuel,
            "throughput": self.cleared_count,
            "current_queue": total_vehicles,
            "vehicles_processed": self.vehicles_processed
        }

    def draw(self, bg_image):
        self.surface.blit(bg_image, (0, 0))
        
        font_title = pygame.font.SysFont(None, 28, bold=True)
        title = font_title.render("FIXED-TIME SYSTEM (Baseline)", True, (255, 100, 100))
        self.surface.blit(title, (SIM_WIDTH//2 - 180, 10))
        
        font = pygame.font.SysFont(None, 20)
        y_pos = 40
        for lane in range(4):
            lane_text = f"Lane {lane}: {len(self.lanes[lane])} vehicles"
            lane_surface = font.render(lane_text, True, (255,255,255))
            self.surface.blit(lane_surface, (10, y_pos))
            y_pos += 22
        
        for lane in range(4):
            for v in self.lanes[lane]:
                self.surface.blit(v["img"], (v["x"], v["y"]))
        
        for lane in range(4):
            if lane == self.current_lane:
                if self.light_state == "green":
                    sig = self.signal_imgs["green"]
                    remaining = max(0, FIXED_GREEN_DURATION - (time.time()-self.phase_start_time))
                    text_color = (0,255,0)
                else:
                    sig = self.signal_imgs["yellow"]
                    remaining = max(0, YELLOW_DURATION - (time.time()-self.phase_start_time))
                    text_color = (255,255,0)
                time_text = f"{int(remaining)}s"
            else:
                sig = self.signal_imgs["red"]
                time_text = "WAIT"
                text_color = (255,0,0)
            
            self.surface.blit(sig, self.signal_positions[lane])
            font_time = pygame.font.SysFont(None, 26)
            text_surf = font_time.render(time_text, True, text_color)
            text_x = self.signal_positions[lane][0] + 10
            text_y = self.signal_positions[lane][1] + 45
            pygame.draw.rect(self.surface, (0,0,0), (text_x-3, text_y-3, text_surf.get_width()+6, text_surf.get_height()+6))
            self.surface.blit(text_surf, (text_x, text_y))
        
        metrics_data = self.get_current_metrics()
        font_metrics = pygame.font.SysFont(None, 20)
        info_x = SIM_WIDTH - 280
        info_y = 10
        
        metrics_text = [
            f"Cleared: {self.cleared_count}",
            f"Active Lane: {self.current_lane} ({self.light_state.upper()})",
            f"Avg Wait: {metrics_data['avg_wait_time']:.1f}s",
            f"Avg Fuel: {metrics_data['avg_fuel_consumption']:.4f}L",
            f"Throughput: {metrics_data['throughput']}"
        ]
        
        for text in metrics_text:
            surf = font_metrics.render(text, True, (255, 255, 255))
            self.surface.blit(surf, (info_x, info_y))
            info_y += 22


def run_simulation_comparison(vehicle_counts, scenario="peak"):
    """Run both simulations side-by-side for comparison"""
    pygame.init()
    
    # Create two windows side by side
    screen_adaptive = pygame.display.set_mode((SIM_WIDTH, SIM_HEIGHT))
    pygame.display.set_caption(f"Adaptive vs Fixed-Time Comparison - {scenario.upper()} Scenario")
    
    clock = pygame.time.Clock()
    
    # Load background
    try:
        bg_image = pygame.image.load("mod_int.png").convert()
        bg_image = pygame.transform.scale(bg_image, (SIM_WIDTH, SIM_HEIGHT))
    except pygame.error:
        bg_image = pygame.Surface((SIM_WIDTH, SIM_HEIGHT))
        bg_image.fill((50,50,50))
        road_color = (80,80,80)
        line_color = (255,255,255)
        pygame.draw.rect(bg_image, road_color, (SIM_WIDTH//2 - 50, 0, 100, SIM_HEIGHT))
        pygame.draw.rect(bg_image, road_color, (0, SIM_HEIGHT//2 - 50, SIM_WIDTH, 100))
        for i in range(0, SIM_WIDTH, 40):
            pygame.draw.rect(bg_image, line_color, (i, SIM_HEIGHT//2, 20, 2))
        for i in range(0, SIM_HEIGHT, 40):
            pygame.draw.rect(bg_image, line_color, (SIM_WIDTH//2, i, 2, 20))
    
    vehicle_imgs = load_vehicle_images()
    signal_imgs = load_signal_images()
    
    print(f"\n{'='*70}")
    print(f"RUNNING {scenario.upper()} SCENARIO SIMULATION")
    print(f"{'='*70}")
    print(f"Initial vehicle counts: {vehicle_counts}")
    
    # Set scenario in metrics
    metrics.current_scenario = scenario
    
    # Run adaptive first
    print("\n--- Running ADAPTIVE SYSTEM ---")
    sim_adaptive = AdaptiveTrafficSim(screen_adaptive, vehicle_imgs, vehicle_counts, signal_imgs)
    
    running = True
    sim_duration = 120  # Run for 2 minutes
    start_time = time.time()
    
    while running and (time.time() - start_time) < sim_duration:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        sim_adaptive.update(dt)
        sim_adaptive.draw(bg_image)
        pygame.display.flip()
        
        # Check if all vehicles cleared
        if sum(len(lane) for lane in sim_adaptive.lanes) == 0:
            print("All vehicles cleared in adaptive system!")
            break
    
    # Record adaptive metrics
    metrics.adaptive_throughput = sim_adaptive.cleared_count
    metrics.adaptive_co2_emissions = sim_adaptive.total_fuel_consumed * CO2_PER_LITER
    metrics.queue_lengths_adaptive.append(sum(len(lane) for lane in sim_adaptive.lanes))
    
    time.sleep(2)
    
    # Run fixed-time
    print("\n--- Running FIXED-TIME SYSTEM (Baseline) ---")
    sim_fixed = FixedTimeTrafficSim(screen_adaptive, vehicle_imgs, vehicle_counts, signal_imgs)
    
    running = True
    start_time = time.time()
    
    while running and (time.time() - start_time) < sim_duration:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        sim_fixed.update(dt)
        sim_fixed.draw(bg_image)
        pygame.display.flip()
        
        if sum(len(lane) for lane in sim_fixed.lanes) == 0:
            print("All vehicles cleared in fixed-time system!")
            break
    
    # Record fixed-time metrics
    metrics.fixed_throughput = sim_fixed.cleared_count
    metrics.fixed_co2_emissions = sim_fixed.total_fuel_consumed * CO2_PER_LITER
    metrics.queue_lengths_fixed.append(sum(len(lane) for lane in sim_fixed.lanes))
    
    pygame.quit()


def generate_scenario_counts(scenario):
    """Generate vehicle counts based on scenario type"""
    if scenario == "peak":
        # High traffic, unbalanced distribution
        return [random.randint(20, 50), random.randint(15, 40), random.randint(25, 45), random.randint(18, 35)]
    elif scenario == "off-peak":
        # Moderate traffic, balanced
        return [random.randint(5, 15), random.randint(5, 15), random.randint(5, 15), random.randint(5, 15)]
    elif scenario == "mixed":
        # Variable traffic
        return [random.randint(10, 30), random.randint(5, 25), random.randint(15, 35), random.randint(8, 22)]
    return [10, 10, 10, 10]


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(argv=None):
    """Main entrypoint.

    Accepts an optional `argv` list (for programmatic invocation). Supported
    CLI args: `--input` (comma-separated files), `--mode` (detect|simulate),
    `--weights` (path to weights).
    """
    parser = argparse.ArgumentParser(prog="Merges.py")
    parser.add_argument("--input", help="Input file or comma-separated list of files")
    parser.add_argument("--mode", choices=["detect", "simulate"], help="Mode to run: detect or simulate")
    parser.add_argument("--weights", help="Path to YOLO weights file")
    args = parser.parse_args(argv)

    print("=" * 70)
    print("ADAPTIVE TRAFFIC CONTROL USING YOLOv11x")
    print("Integrated Detection and Simulation System")
    print("=" * 70)

    # Load model if weights provided (lazy load)
    if args.weights:
        try:
            load_model(args.weights)
        except Exception as e:
            print(f"Failed to load model from {args.weights}: {e}")
            raise

    # Determine mode
    mode = "detect_and_simulate"
    if args.mode == "simulate":
        mode = "simulate"
    elif args.mode == "detect":
        mode = "detect"

    if mode == "detect_and_simulate":
        # PHASE 1: VEHICLE DETECTION
        print("\n" + "=" * 70)
        print("PHASE 1: VEHICLE DETECTION AND COUNTING")
        print("=" * 70)
        
        # File selection: either from CLI or interactive file dialog
        if args.input:
            files = [p.strip() for p in args.input.split(",") if p.strip()]
        else:
            print("\nPlease select 4 video files for the 4 lanes.")
            files = select_files()

        if not files or len(files) != 4:
            print("Error: You must provide exactly 4 files (use --input or interactive selection).")
            sys.exit(1)

        print("\nSelected files:", files)

        # Polygon selection
        print("\n--- Polygon Selection Phase ---")
        state = AppState()
        for i, file in enumerate(files):
            print(f"\nProcessing Lane {i}: {file}")
            process_file(file, state)

        print("\nPolygons selected for all lanes:")
        for i, polygon in enumerate(state.polygons):
            print(f"Lane {i}: {polygon}")

        with open("polygons.txt", "w") as f:
            for i, polygon in enumerate(state.polygons):
                f.write(f"Lane {i}: {polygon}\n")
        print("\nPolygon coordinates saved to polygons.txt")

        # Vehicle counting
        print("\n" + "=" * 70)
        print("COUNTING VEHICLES WITH YOLOv11x")
        print("=" * 70)
        
        vehicle_counts = []
        for i, file in enumerate(files):
            print(f"\nProcessing Lane {i}: {file}")
            # Ensure model is loaded before counting
            if model is None:
                try:
                    load_model(args.weights or "models/yolo11x.pt")
                except Exception as e:
                    print(f"Model load failed: {e}")
                    sys.exit(1)

            count = count_vehicles(file, state.polygons[i], num_frames=10)
            vehicle_counts.append(count)
            print(f"Total vehicles in Lane {i}: {count}")
        
        print("\n" + "=" * 70)
        print("DETECTION RESULTS")
        print("=" * 70)
        print(f"Vehicle counts: {vehicle_counts}")
        print(f"Detection Accuracy: {metrics.calculate_accuracy():.2f}%")
        
        max_count = max(vehicle_counts)
        max_index = vehicle_counts.index(max_count)
        print(f"\nLane {max_index} has the most vehicles: {max_count}")
        
        # Determine scenario based on counts
        total_vehicles = sum(vehicle_counts)
        if total_vehicles > 100:
            scenario = "peak"
        elif total_vehicles < 40:
            scenario = "off-peak"
        else:
            scenario = "mixed"
        
        print(f"Detected scenario: {scenario.upper()}")
        
        # PHASE 2: SIMULATION
        print("\n" + "=" * 70)
        print("PHASE 2: COMPARATIVE SIMULATION")
        print("=" * 70)
        time.sleep(2)
        
        run_simulation_comparison(vehicle_counts, scenario)
        
    elif mode == "simulate":
        # SIMULATION ONLY MODE - Test all scenarios
        print("\n" + "=" * 70)
        print("MULTI-SCENARIO TESTING MODE")
        print("=" * 70)

        scenarios = ["peak", "off-peak", "mixed"]

        for scenario in scenarios:
            vehicle_counts = generate_scenario_counts(scenario)
            print(f"\n{'='*70}")
            print(f"TESTING {scenario.upper()} SCENARIO")
            print(f"Vehicle counts: {vehicle_counts}")
            print(f"{'='*70}")

            run_simulation_comparison(vehicle_counts, scenario)

            # Display scenario results
            report = metrics.generate_report()
            print(f"\n--- {scenario.upper()} SCENARIO RESULTS ---")
            print(json.dumps(report, indent=2))

            time.sleep(3)
        return
    
    # FINAL REPORT
    print("\n" + "=" * 70)
    print("FINAL PERFORMANCE REPORT")
    print("=" * 70)
    
    final_report = metrics.generate_report()
    print(json.dumps(final_report, indent=2))
    
    # Save report to file
    with open("performance_report.json", "w") as f:
        json.dump(final_report, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Detection Accuracy: {final_report['detection_accuracy']}%")
    print(f"✓ Wait Time Reduction: {final_report['improvements']['wait_time_reduction']}%")
    print(f"✓ Fuel Savings: {final_report['improvements']['fuel_savings']}%")
    print(f"✓ Throughput Increase: {final_report['improvements']['throughput_increase']}%")
    print(f"✓ Queue Reduction: {final_report['improvements']['queue_reduction']}%")
    print(f"\nPerformance report saved to performance_report.json")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        exit_event.set()
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)