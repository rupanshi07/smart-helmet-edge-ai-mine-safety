"""
edge_node.py

Edge ML (TinyML-style) hazard detection running on a wearable node.
Designed for mining/construction safety simulation.
"""

from collections import deque


class EdgeMLNode:
    def __init__(self, node_id):
        self.node_id = node_id

        # Safety thresholds (domain-inspired)
        self.fall_accel_threshold = 3.5
        self.gas_threshold = 100.0
        self.vibration_threshold = 0.3

        # Temporal smoothing buffers (very lightweight)
        self.gas_window = deque(maxlen=2)
        self.accel_window = deque(maxlen=2)
        self.vibration_window = deque(maxlen=2)

    def extract_features(self, sensor_data):
        """
        Feature extraction stage (what TinyML would see).
        """
        return {
            "accel": sensor_data["accel"],
            "gas": sensor_data["gas"],
            "vibration": sensor_data["vibration"]
        }

    def smooth(self, window, value):
        """
        Simple moving average smoothing.
        """
        window.append(value)
        return sum(window) / len(window)

    def infer(self, features):
        """
        Rule-based inference (explainable Edge ML).
        """
        avg_accel = self.smooth(self.accel_window, features["accel"])
        avg_gas = self.smooth(self.gas_window, features["gas"])
        avg_vib = self.smooth(self.vibration_window, features["vibration"])

        # Priority-based decision logic
        if avg_accel < self.fall_accel_threshold:
            return "fall"

        if avg_gas > self.gas_threshold:
            return "gas_spike"

        if avg_vib > self.vibration_threshold:
            return "vibration"

        return "normal"

    def process(self, sensor_data, current_time):
        """
        Full Edge ML pipeline:
        sensor → features → inference → alert
        """
        features = self.extract_features(sensor_data)
        decision = self.infer(features)

        if decision != "normal":
            return {
                "node_id": self.node_id,
                "time": current_time,
                "event": decision,
                "confidence": 0.9,
                "source": "edge"
            }

        return None
