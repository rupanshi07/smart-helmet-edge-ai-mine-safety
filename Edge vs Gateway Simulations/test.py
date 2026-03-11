from sensors import SensorSimulator
from events import EventInjector

sensor = SensorSimulator()
events = EventInjector()

events.trigger_event("gas_spike", start_time=3)

for t in range(7):
    data = sensor.read_all()
    data = events.apply_event(data, t)
    print(f"t={t}", data)
