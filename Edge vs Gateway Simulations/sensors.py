"""
sensors.py

Simulates raw sensor readings for underground worker devices.
Used by both Edge ML and Central ML workflows.
"""

import random
import math


class SensorSimulator:
    def __init__(self):
        # Baseline values
        self.base_gas_ppm = 30.0
        self.base_vibration = 0.02
        self.base_accel = 9.8  # m/s^2 (gravity)

    def read_imu(self):
        """
        Simulate accelerometer magnitude (m/s^2)
        """
        noise = random.gauss(0, 0.2)
        accel_mag = self.base_accel + noise
        return accel_mag

    def read_gas(self):
        """
        Simulate gas concentration (ppm)
        """
        noise = random.gauss(0, 1.5)
        gas_ppm = max(0.0, self.base_gas_ppm + noise)
        return gas_ppm

    def read_vibration(self):
        """
        Simulate vibration RMS value
        """
        noise = random.gauss(0, 0.005)
        vibration = max(0.0, self.base_vibration + noise)
        return vibration

    def read_all(self):
        """
        Read all sensors at once
        """
        return {
            "accel": self.read_imu(),
            "gas": self.read_gas(),
            "vibration": self.read_vibration()
        }
