from config import *
from node import Node
from gateway import Gateway
from lora_channel import LoRaChannel
from utils import init_stats
import pandas as pd

node = Node()
gateway = Gateway()
channel = LoRaChannel(LORA_BASE_LOSS)

stats = init_stats()

for t in range(0, SIM_TIME, TIME_STEP):
    packet, emergency = node.generate_packet(t)

    if packet:
        stats["packets_sent"] += 1
        rx = channel.transmit(packet)
    else:
        rx = None

    if rx:
        stats["packets_received"] += 1
        gateway.process(rx)
    elif emergency:
        stats["events_missed"] += 1

df = pd.DataFrame([stats])
df["architecture"] = ARCH_MODE
df.to_csv(f"results_{ARCH_MODE.lower()}.csv", index=False)

print(df)
