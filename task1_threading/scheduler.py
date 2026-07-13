"""
Task 1 - Part B: Round-Robin CPU Scheduler Simulation
ST5004CEM Operating Systems and Security

This program simulates the Round-Robin CPU scheduling algorithm used by
operating systems to give every process a fair, time-sliced share of the
CPU. It is a SIMULATION - it does not create real OS processes, it models
how the scheduler would allocate CPU time among a set of processes.

For each process it computes:
    - Completion Time (CT)
    - Turnaround Time (TAT) = CT - Arrival Time
    - Waiting Time (WT)     = TAT - Burst Time
It also prints a text-based Gantt chart showing the execution order.
"""

from collections import deque


class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time          # total CPU time required
        self.remaining_time = burst_time       # time left to execute
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0


def round_robin_schedule(processes, quantum):
    """
    Simulates round-robin scheduling.

    processes : list of Process objects (will be scheduled by arrival_time)
    quantum   : the fixed time slice given to each process per turn

    Returns the Gantt chart as a list of (pid, start_time, end_time) tuples.
    """
    processes = sorted(processes, key=lambda p: p.arrival_time)
    n = len(processes)
    ready_queue = deque()
    gantt_chart = []

    current_time = 0
    completed = 0
    in_queue = [False] * n
    i = 0  # pointer into processes sorted by arrival time

    # Prime the queue with any processes that have already arrived at t=0
    while i < n and processes[i].arrival_time <= current_time:
        ready_queue.append(processes[i])
        in_queue[i] = True
        i += 1

    if not ready_queue and n > 0:
        # No process has arrived yet, jump time forward to the first arrival
        current_time = processes[0].arrival_time
        while i < n and processes[i].arrival_time <= current_time:
            ready_queue.append(processes[i])
            in_queue[i] = True
            i += 1

    while completed < n:
        process = ready_queue.popleft()

        run_time = min(quantum, process.remaining_time)
        start = current_time
        current_time += run_time
        process.remaining_time -= run_time
        gantt_chart.append((process.pid, start, current_time))

        # Any processes that arrived DURING this time slice join the queue
        # before the process we just ran (if it still needs more time) goes
        # back in, matching standard round-robin queue behaviour.
        while i < n and processes[i].arrival_time <= current_time:
            ready_queue.append(processes[i])
            in_queue[i] = True
            i += 1

        if process.remaining_time > 0:
            ready_queue.append(process)
        else:
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            completed += 1

        # If the queue is empty but processes remain (a gap / idle CPU time),
        # fast-forward the clock to the next arrival.
        if not ready_queue and completed < n:
            current_time = processes[i].arrival_time
            while i < n and processes[i].arrival_time <= current_time:
                ready_queue.append(processes[i])
                in_queue[i] = True
                i += 1

    return gantt_chart


def print_gantt_chart(gantt_chart):
    print("\nGantt Chart:")
    top = "|"
    bottom = "0"
    for pid, start, end in gantt_chart:
        width = max(len(str(pid)), len(str(end))) + 2
        top += f" {pid} ".center(width - 1) + "|"
        bottom += str(end).rjust(width)
    print(top)
    print(bottom)


def print_results(processes):
    print("\n{:<6}{:<10}{:<10}{:<12}{:<10}{:<10}".format(
        "PID", "Arrival", "Burst", "Completion", "Turnaround", "Waiting"))
    total_wt = 0
    total_tat = 0
    for p in sorted(processes, key=lambda x: x.pid):
        print("{:<6}{:<10}{:<10}{:<12}{:<10}{:<10}".format(
            p.pid, p.arrival_time, p.burst_time,
            p.completion_time, p.turnaround_time, p.waiting_time))
        total_wt += p.waiting_time
        total_tat += p.turnaround_time

    n = len(processes)
    print(f"\nAverage Waiting Time    : {total_wt / n:.2f}")
    print(f"Average Turnaround Time : {total_tat / n:.2f}")


if __name__ == "__main__":
    # Example process set - feel free to change these values or take
    # input from the user instead.
    QUANTUM = 4

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=10),
        Process(pid="P2", arrival_time=1, burst_time=5),
        Process(pid="P3", arrival_time=2, burst_time=8),
        Process(pid="P4", arrival_time=3, burst_time=6),
    ]

    print("=" * 70)
    print(f"ROUND-ROBIN SCHEDULING SIMULATION (Time Quantum = {QUANTUM})")
    print("=" * 70)
    print("\nInput Processes:")
    print("{:<6}{:<10}{:<10}".format("PID", "Arrival", "Burst"))
    for p in processes:
        print("{:<6}{:<10}{:<10}".format(p.pid, p.arrival_time, p.burst_time))

    gantt_chart = round_robin_schedule(processes, QUANTUM)
    print_gantt_chart(gantt_chart)
    print_results(processes)
