from edge_node import EdgeMLNode

class CentralMLNode:
    """
    Centralized ML running at the gateway.
    Uses the same logic as Edge ML but operates
    only on received (possibly incomplete) data.
    """

    def __init__(self, node_id=0):
        self.node_id = node_id
        self.model = EdgeMLNode(node_id=node_id)
        self.alerts = []

    def receive_and_process(self, packet):
        """
        packet: {
            'time': int,
            'sensor_data': dict
        }
        """
        if packet is None:
            return None

        t = packet["time"]
        data = packet["sensor_data"]

        alert = self.model.process(data, t)

        if alert:
            alert["source"] = "central"
            self.alerts.append(alert)
            return alert

        return None
