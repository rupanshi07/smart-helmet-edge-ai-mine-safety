from lora_channel import LoRaChannel

lora = LoRaChannel(packet_loss_prob=0.4)

for i in range(10):
    pkt = {"time": i, "data": "sensor_data"}
    rx = lora.transmit(pkt)

    if rx:
        print("📡 RECEIVED:", rx)
    else:
        print("❌ LOST packet at t =", i)
