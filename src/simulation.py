from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Callable, List
import random

import numpy as np

from ftsp import Node

SPEED_OF_LIGHT = 299_792_458


@dataclass(order=True)
class Event:
    time: float
    handler: Callable = field(compare=False)


@dataclass(init=False)
class StatPoint:
    real_time: float
    total_nodes: int
    synced_count: int
    root_claimants: List[int]
    prediction_error: List[float]

    def __init__(self, nodes, real_time):
        self.real_time = real_time
        self.root_claimants = [node.node_id for node in nodes if node.is_root()]
        self.total_nodes = len(nodes)
        self.synced_count = sum(node.is_synced() for node in nodes)
        if self.root_claimants:
            actual_root = sorted(self.root_claimants)[0]
            self.prediction_error = [
                abs(
                    node.predict_time(real_time)
                    - nodes[actual_root].predict_time(real_time)
                )
                for node in nodes
                if node.is_synced()
            ]
        else:
            self.prediction_error = []


def random_with_diameter(span: float) -> float:
    return random.uniform(-span / 2, span / 2)


def normal(mean: float, sigma: float) -> float:
    return np.random.normal(mean, sigma)


def get_n_closest(n: int, node: Node, nodes: List[Node]) -> List[Node]:
    closest = sorted(nodes, key=lambda neighbour: node.distance_to(neighbour))
    return closest[1 : n + 1]


def simulate(
    n: int,
    simulation_length: float,
    delay_mean: float,
    delay_sigma: float,
    offset_sigma: float,
    skew_sigma: float,
    connect_closest=5,
    area_diameter=1_000_000,
    stats_every: float = 1.0,
    debug_print: bool = False,
) -> List[StatPoint]:
    print(f"Simulating with {n} nodes")
    np.random.seed(0)
    nodes = [
        Node(
            node_id=i,
            clock_offset=normal(0, offset_sigma),
            clock_skew=normal(1, skew_sigma),
            x=random_with_diameter(area_diameter),
            y=random_with_diameter(area_diameter),
        )
        for i in range(0, n)
    ]
    neighbours = {node: get_n_closest(connect_closest, node, nodes) for node in nodes}

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
        distance_delay = sender.distance_to(reciever) / SPEED_OF_LIGHT
        random_delay = max(0, np.random.normal(delay_mean, delay_sigma))
        return distance_delay + random_delay

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
        return StatPoint(nodes, real_time)

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
