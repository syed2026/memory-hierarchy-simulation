import random

class MemoryLevel:
    def __init__(self, name, size, latency):
        self.name = name
        self.size = size
        self.latency = latency
        self.storage = []

    def is_full(self):
        return len(self.storage) >= self.size

    def access(self, data):
        if data in self.storage:
            self.storage.remove(data)
            self.storage.append(data)
            return True
        return False

    def add(self, data):
        if data in self.storage:
            self.storage.remove(data)
            self.storage.append(data)
            return

        if self.is_full():
            evicted = self.storage.pop(0)
            print(f"[LRU EVICT] {self.name}: Removed {evicted}")

        self.storage.append(data)

    def remove(self):
        if self.storage:
            return self.storage.pop(0)
        return None

    def __str__(self):
        return f"{self.name}: {self.storage}"


class Transfer:
    def __init__(self, source, destination, data, remaining_cycles):
        self.source = source
        self.destination = destination
        self.data = data
        self.remaining_cycles = remaining_cycles


class MemorySystem:
    def __init__(self, bandwidth=2):
        self.ssd = MemoryLevel("SSD", 20, latency=3)
        self.dram = MemoryLevel("DRAM", 15, latency=2)
        self.l3 = MemoryLevel("L3", 10, latency=2)
        self.l2 = MemoryLevel("L2", 6, latency=1)
        self.l1 = MemoryLevel("L1", 3, latency=1)

        self.clock = 0
        self.bandwidth = bandwidth
        self.in_flight = []

    def load_ssd(self):
        for i in range(1, 21):
            self.ssd.add(i)

    def schedule_transfer(self, source, destination):
        data = source.remove()
        if data is not None:
            transfer = Transfer(source, destination, data, source.latency)
            self.in_flight.append(transfer)
            print(f"[SCHEDULED] {source.name} -> {destination.name}: {data}")

    def process_transfers(self):
        completed = []
        for t in self.in_flight:
            t.remaining_cycles -= 1
            if t.remaining_cycles <= 0:
                t.destination.add(t.data)
                print(f"[COMPLETE] {t.source.name} -> {t.destination.name}: {t.data}")
                completed.append(t)

        for t in completed:
            self.in_flight.remove(t)

    def run_cycle(self):
        self.clock += 1
        print(f"\n===== CLOCK {self.clock} =====")

        transfers = 0
        levels = [
            (self.ssd, self.dram),
            (self.dram, self.l3),
            (self.l3, self.l2),
            (self.l2, self.l1),
        ]

        for src, dst in levels:
            if transfers >= self.bandwidth:
                break
            if src.storage:
                self.schedule_transfer(src, dst)
                transfers += 1

        self.process_transfers()

    def read(self, instruction):
        print(f"\n[READ] {instruction}")

        if self.l1.access(instruction):
            print("L1 HIT")
        elif self.l2.access(instruction):
            print("L2 HIT")
            self.l1.add(instruction)
        elif self.l3.access(instruction):
            print("L3 HIT")
            self.l2.add(instruction)
            self.l1.add(instruction)
        elif self.dram.access(instruction):
            print("DRAM HIT")
            self.l3.add(instruction)
            self.l2.add(instruction)
            self.l1.add(instruction)
        elif self.ssd.access(instruction):
            print("MISS -> Fetch from SSD")
            self.dram.add(instruction)
            self.l3.add(instruction)
            self.l2.add(instruction)
            self.l1.add(instruction)
        else:
            print("Not Found")

    def write_back(self, instruction):
        print(f"\n[WRITE BACK] {instruction}")

        self.l1.add(instruction)
        self.l2.add(instruction)
        self.l3.add(instruction)
        self.dram.add(instruction)
        self.ssd.add(instruction)

    def print_state(self):
        print("\n===== FINAL STATE =====")
        print(self.ssd)
        print(self.dram)
        print(self.l3)
        print(self.l2)
        print(self.l1)


if __name__ == "__main__":
    system = MemorySystem()
    system.load_ssd()

    for _ in range(6):
        system.run_cycle()

    system.read(5)
    system.read(10)
    system.read(30)

    system.write_back(99)

    system.print_state()
