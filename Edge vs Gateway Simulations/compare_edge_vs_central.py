from sensors import SensorSimulator
from events import EventInjector
from edge_node import EdgeMLNode
from central_node import CentralMLNode
from lora_channel import LoRaChannel

SIM_TIME = 30
PACKET_LOSS = 0.4

print("\n=== EDGE vs CENTRAL ML COMPARISON ===\n")

# Initialize components
sensor = SensorSimulator()
events = EventInjector()

edge_node = EdgeMLNode(node_id=1)
central_node = CentralMLNode(node_id=1)
lora = LoRaChannel(packet_loss_prob=PACKET_LOSS)

# Inject hazard
events.trigger_event("gas_spike", start_time=10)

# Metrics
edge_alerts = []
central_alerts = []

packets_sent = 0
packets_received = 0

for t in range(SIM_TIME):
    # Read sensors
    data = sensor.read_all()
    events.apply_event(data, current_time=t)

    # ---------- EDGE ML ----------
    edge_alert = edge_node.process(data, t)
    if edge_alert:
        edge_alerts.append(edge_alert)

    # ---------- CENTRAL ML ----------
    packet = {
        "time": t,
        "sensor_data": data
    }
    packets_sent += 1
    rx_packet = lora.transmit(packet)

    if rx_packet:
        packets_received += 1
        central_alert = central_node.receive_and_process(rx_packet)
        if central_alert:
            central_alerts.append(central_alert)

# ---------- RESULTS ----------
print("\n--- RESULTS ---")

def summarize(alerts, label):
    if not alerts:
        print(f"{label}: ❌ NO ALERTS")
        return

    first = alerts[0]["time"]
    total = len(alerts)

    print(f"{label}:")
    print(f"  First alert time : {first}")
    print(f"  Total alerts    : {total}")

summarize(edge_alerts, "EDGE ML")
summarize(central_alerts, "CENTRAL ML")

print("\n--- COMMUNICATION ---")
print(f"Packets sent     : {packets_sent}")
print(f"Packets received : {packets_received}")
print(f"Packet loss rate : {(1 - packets_received/packets_sent):.2f}")
