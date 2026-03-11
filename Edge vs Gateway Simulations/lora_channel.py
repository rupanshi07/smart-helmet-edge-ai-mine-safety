import random
import time

class LoRaChannel:
    """
    Simulates a lossy LoRa communication channel.
    """

    def __init__(self,
                 packet_loss_prob=0.3,
                 min_latency=0.2,
                 max_latency=1.5):
        """
        packet_loss_prob: probability that a packet is lost
        latency: transmission delay in seconds
        """
        self.packet_loss_prob = packet_loss_prob
        self.min_latency = min_latency
        self.max_latency = max_latency

    def transmit(self, packet):
        """
        Transmit packet through LoRa.
        Returns packet if received, None if lost.
        """
        # Simulate delay
        delay = random.uniform(self.min_latency, self.max_latency)
        time.sleep(delay)

        # Simulate packet loss
        if random.random() < self.packet_loss_prob:
            return None  # packet lost

        return packet
