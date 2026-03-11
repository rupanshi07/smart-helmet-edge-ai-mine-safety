from sensors import SensorSimulator
from events import EventInjector
from lora_channel import LoRaChannel
from central_node import CentralMLNode

print("\nRunning Central ML test...\n")

sensor = SensorSimulator()
events = EventInjector()
lora = LoRaChannel(packet_loss_prob=0.4)
central = CentralMLNode(node_id=1)

# Inject gas spike at t=3
events.trigger_event("gas_spike", 3)

for t in range(10):
    # Read all sensors
    data = sensor.read_all()

    # Apply event effects with correct time
    events.apply_event(data, current_time=t)

    packet = {
        "time": t,
        "sensor_data": data
    }

    rx_packet = lora.transmit(packet)
    alert = central.receive_and_process(rx_packet)

    print(f"t={t} sent={data} received={rx_packet is not None}")

    if alert:
        print("🚨 CENTRAL ALERT:", alert)
