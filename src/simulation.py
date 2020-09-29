from ftsp import Node
from queue import PriorityQueue


def simulate(n: int, simulation_length: float):
    print(f"Simulating with {n} nodes")
    nodes = [Node(node_id=i, clock_offset=0, clock_speed=1) for i in range(0, n)]
    neighbours = {node: nodes for node in nodes}

    real_time = 0
    future_events = PriorityQueue()

    # Event handling, they will then be stepped through in time order, possibly adding later events.
    def add_timer_event(node: Node):
        def on_timer_event():
            node.handle_timer(real_time)
            add_timer_event(node)

        timer_event = (node.next_timer_event(real_time), on_timer_event)
        future_events.put(timer_event)

    def add_msg_event(msg, reciever: Node, delay: float):
        def on_msg_event():
            reciever.handle_msg(msg)

        msg_event = (real_time + delay, on_msg_event)
        future_events.put(msg_event)

    # Returns the delay for a message sent from a to its neighbour b.
    def msg_delay(sender: Node, reciever: Node) -> float:
        assert reciever in sender.neighbours
        return 1.0

    # Function given to nodes for broadcasting message.
    def broadcast_msg(msg, sender: Node):
        for reciever in neighbours[sender]:
            add_msg_event(msg, reciever, msg_delay(sender, reciever))

    for node in nodes:
        add_timer_event(node)

    while real_time < simulation_length:
        real_time, f = future_events.get()
        f()
