from ml_model import run_ml
from config import ARCH_MODE

class Gateway:
    def process(self, packet):
        if ARCH_MODE == "CENTRAL" and packet is not None:
            return run_ml(packet["sensor"])
        elif ARCH_MODE == "EDGE":
            return packet["event"]
        return None
