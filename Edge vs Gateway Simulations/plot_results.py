import matplotlib.pyplot as plt

# ==============================
# RESULTS FROM YOUR SIMULATION
# ==============================

# Detection latency (time step of first alert)
edge_latency = 10
central_latency = 11

# Total alerts generated
edge_alerts = 5
central_alerts = 3

# LoRa communication stats
packets_sent = 30
packets_received = 21
packet_loss_rate = (packets_sent - packets_received) / packets_sent


# ==============================
# PLOT 1: DETECTION LATENCY
# ==============================
plt.figure()
plt.bar(["Edge ML", "Central ML"],
        [edge_latency, central_latency])
plt.xlabel("Architecture")
plt.ylabel("First Alert Time (t)")
plt.title("Detection Latency Comparison")
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("latency_comparison.png")
plt.show()


# ==============================
# PLOT 2: TOTAL ALERTS
# ==============================
plt.figure()
plt.bar(["Edge ML", "Central ML"],
        [edge_alerts, central_alerts])
plt.xlabel("Architecture")
plt.ylabel("Number of Alerts")
plt.title("Total Hazard Alerts Generated")
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("alerts_comparison.png")
plt.show()


# ==============================
# PLOT 3: PACKET LOSS
# ==============================
plt.figure()
plt.bar(["Packet Loss Rate"], [packet_loss_rate])
plt.ylim(0, 1)
plt.ylabel("Loss Rate")
plt.title("LoRa Communication Packet Loss")
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("packet_loss.png")
plt.show()
