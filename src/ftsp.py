from dataclasses import dataclass, field
from math import sqrt
from typing import List

import numpy as np
from scipy.linalg import lstsq

RESYNC_TIME = 30
MAX_ENTRIES = 10
NUMENTRIES_LIMIT = 3
ROOT_TIMEOUT = 6
TIME_ERROR_LIMIT = 0.001


@dataclass
class SyncMessage:
    send_time: float
    root_id: int
    seq_num: int


@dataclass
class Node:
    node_id: int
    clock_offset: float
    clock_skew: float
    x: float
    y: float

    root_id: int = None
    highest_seq_num: int = 0
    heartbeats: int = 0
    entries: List = field(default_factory=list)
    predicted_offset: float = 0
    predicted_skew: float = 1

    def __hash__(self):
        return self.node_id

    def local_clock(self, real_time: float) -> float:
        return self.clock_offset + real_time * self.clock_skew

    def real_clock(self, local_time: float) -> float:
        return (local_time - self.clock_offset) / self.clock_skew

    def predict_time(self, real_time):
        return self.local_clock(real_time) * self.predicted_skew + self.predicted_offset

    def is_root(self):
        return self.root_id == self.node_id

    def is_synced(self):
        # TODO: is this correct?
        return len(self.entries) >= NUMENTRIES_LIMIT or self.is_root()

    def distance_to(self, other) -> float:
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return sqrt(dx * dx + dy * dy)

    def calculate_regression(self):
        # Do linear regression on all pairs (local, global) we have to estimate skew and offset.
        self.entries = self.entries[-MAX_ENTRIES:]
        local_times, global_times = zip(*self.entries)
        A = np.stack([np.array(local_times), np.ones(len(self.entries))], axis=1)
        b = np.array(global_times)
        # self.predicted_skew, self.predicted_offset = lstsq(A, b)[0]

    def get_error_for_msg(self, real_time, msg):
        return self.predict_time(real_time) - msg.send_time

    def next_timer_event(self, real_time: float) -> float:
        local_time = self.local_clock(real_time) + 1e-9
        local_time_until_event = RESYNC_TIME - (local_time % RESYNC_TIME)
        return self.real_clock(local_time + local_time_until_event)

    def handle_timer(self, real_time, send):
        self.heartbeats += 1

        # If we haven't heard from anyone with lower root, nominate ourselves as root.
        if self.root_id != self.node_id and self.heartbeats >= ROOT_TIMEOUT:
            self.root_id = self.node_id

        if len(self.entries) > NUMENTRIES_LIMIT or self.root_id == self.node_id:
            send(
                SyncMessage(
                    self.predict_time(real_time), self.root_id, self.highest_seq_num
                ),
                self,
            )

        if self.root_id == self.node_id:
            self.highest_seq_num += 1

    def handle_msg(self, real_time, msg: SyncMessage):
        if self.root_id is None or msg.root_id < self.root_id:
            self.root_id = msg.root_id
        elif msg.root_id > self.root_id or msg.seq_num <= self.highest_seq_num:
            return

        self.highest_seq_num = msg.seq_num
        if self.root_id < self.node_id:
            self.heartbeats = 0

        if (
            len(self.entries) >= NUMENTRIES_LIMIT
            and self.get_error_for_msg(real_time, msg) > TIME_ERROR_LIMIT
        ):
            self.entries = []
        else:
            new_entry = (self.local_clock(real_time), msg.send_time)
            self.entries.append(new_entry)
            self.calculate_regression()
