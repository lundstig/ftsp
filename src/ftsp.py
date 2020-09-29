from dataclasses import dataclass

RESYNC_TIME = 30
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
    clock_speed: float

    root_id: int = None
    highest_seq_num: int = 0
    heartbeats: int = 0
    entries: List = []

    def local_clock(self, real_time: float) -> float:
        return self.clock_offset + real_time * self.clock_speed

    def real_clock(self, local_time: float) -> float:
        return (local_time - self.clock_offset) / self.clock_speed

    def predict_time(self, real_time):
        pass

    def estimate_drift(self, real_time, msg):
        pass

    def get_error(self, real_time, msg):
        return self.predict_time(real_time) - msg

    def next_timer_event(self, real_time: float) -> float:
        local_time = self.local_clock(real_time)
        local_time_until_event = local_time % RESYNC_TIME
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
                )
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
            and self.get_error(real_time, msg) > TIME_ERROR_LIMIT
        ):
            self.entries = []
        else:
            self.entries.append(msg)
            self.estimate_drift(real_time, msg)
