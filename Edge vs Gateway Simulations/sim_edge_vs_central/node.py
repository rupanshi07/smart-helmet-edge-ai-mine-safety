import random
from ml_model import run_ml
from config import ARCH_MODE, EDGE_PACKET_SIZE, CENTRAL_PACKET_SIZE

class Node:
    def read_sensors(self):
        gas = random.gauss(25, 5)
        acc = random.gauss(1, 0.2)
        gyro = random.gauss(0.5, 0.1)

        emergency = random.random() < 0.05
        if emergency:
            gas += 100
            acc += 3

        return gas, acc, gyro, emergency

    def generate_packet(self, t):
        gas, acc, gyro, emergency = self.read_sensors()

        if ARCH_MODE == "EDGE":
            label = run_ml((gas, acc, gyro))
            if label == 0:
                return None, emergency
            return {
                "time": t,
                "event": label,
                "size": EDGE_PACKET_SIZE
            }, emergency

        else:
            return {
                "time": t,
                "sensor": (gas, acc, gyro),
                "size": CENTRAL_PACKET_SIZE
            }, emergency
