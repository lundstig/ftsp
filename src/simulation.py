from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import Callable, List

from ftsp import Node


@dataclass(order=True)
class Event:
    time: float
    handler: Callable = field(compare=False)


@dataclass
class StatPoint:
    time: float
    prediction_errors: List[float]


def simulate(
    n: int,
    simulation_length: float,
    stats_every: float = 1.0,
    debug_print: bool = False,
) -> List[StatPoint]:
    print(f"Simulating with {n} nodes")
    nodes = [Node(node_id=i, clock_offset=0, clock_skew=1) for i in range(0, n)]
    neighbours = {node: nodes for node in nodes}

    real_time = 0
    future_events = PriorityQueue()

    # Event handling, they will then be stepped through in time order, possibly adding later events.
    def add_timer_event(node: Node):
        def on_timer_event():
            if debug_print:
                print(f"{real_time}: Timer for {node.node_id}")
            node.handle_timer(real_time, broadcast_msg)
            add_timer_event(node)

        timer_event = Event(node.next_timer_event(real_time), on_timer_event)
        future_events.put(timer_event)

    def add_msg_event(msg, reciever: Node, delay: float):
        def on_msg_event():
            if debug_print:
                print(f"{real_time}: {reciever.node_id} got {msg}")
            reciever.handle_msg(real_time, msg)

        msg_event = Event(real_time + delay, on_msg_event)
        future_events.put(msg_event)

    # Returns the delay for a message sent from a to its neighbour b.
    def msg_delay(sender: Node, reciever: Node) -> float:
        assert reciever in neighbours[sender]
        return 1.0

    # Function given to nodes for broadcasting message.
    def broadcast_msg(msg, sender: Node):
        if debug_print:
            print(f"{real_time}: {sender.node_id} sending {msg}")
        for reciever in neighbours[sender]:
            add_msg_event(msg, reciever, msg_delay(sender, reciever))

    # Function that calculates and stores stats.
    def calc_stats():
        if debug_print:
            print(f"{real_time}: Statistics")
        errors = [
            abs(node.predict_time(real_time) - real_time)
            for node in nodes
            if node.is_synced()
        ]
        return StatPoint(real_time, errors)

    stats = []

    def add_stats_events():
        def on_stats_event():
            stats.append(calc_stats())
            add_stats_events()

        future_events.put(Event(real_time + stats_every, on_stats_event))

    # Setup initial events
    calc_stats()
    add_stats_events()
    for node in nodes:
        add_timer_event(node)

    # Simulate!
    while future_events:
        next_event = future_events.get()
        real_time = next_event.time
        if real_time > simulation_length:
            break
        next_event.handler()
    return stats
