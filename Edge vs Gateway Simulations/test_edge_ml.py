from sensors import SensorSimulator
from events import EventInjector
from edge_node import EdgeMLNode

sensor = SensorSimulator()
events = EventInjector()
edge_node = EdgeMLNode(node_id=1)

# Schedule a gas leak at t=3
events.trigger_event("gas_spike", start_time=3)

print("Running Edge ML test...\n")

for t in range(7):
    data = sensor.read_all()
    data = events.apply_event(data, t)

    alert = edge_node.process(data, t)

    print(f"t={t} data={data}")
    if alert:
        print("   🚨 EDGE ALERT:", alert)
