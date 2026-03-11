import random

class LoRaChannel:
    def __init__(self, base_loss):
        self.base_loss = base_loss

    def transmit(self, packet):
        size_factor = packet["size"] / 12
        loss_prob = min(1.0, self.base_loss * size_factor)

        if random.random() < loss_prob:
            return None
        return packet
