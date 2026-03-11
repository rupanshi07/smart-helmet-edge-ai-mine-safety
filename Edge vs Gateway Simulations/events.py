"""
events.py

Defines hazard events and injects them into sensor readings.
"""

class EventInjector:
    def __init__(self):
        self.active_event = None
        self.event_start_time = None
        self.event_end_time = None

    def trigger_event(self, event_type, start_time, duration=3):
        """
        Schedule a hazard event
        """
        self.active_event = event_type
        self.event_start_time = start_time
        self.event_end_time = start_time + duration

    def apply_event(self, sensor_data, current_time):
        """
        Modify sensor readings based on active event
        """
        if (
            self.active_event
            and self.event_start_time <= current_time <= self.event_end_time
        ):
            if self.active_event == "fall":
                sensor_data["accel"] = 2.0

            elif self.active_event == "gas_spike":
                sensor_data["gas"] += 150.0

            elif self.active_event == "vibration":
                sensor_data["vibration"] += 0.5

        return sensor_data
