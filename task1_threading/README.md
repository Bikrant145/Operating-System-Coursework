# Task 1: Process Management and Threading

## Files
- `sync_demo.py` — Threading, synchronization, race condition, and deadlock prevention demo
- `scheduler.py` — Round-robin CPU scheduler simulation
- `screenshots/` — Output screenshots from running both programs

## Requirements
- Python 3.8 or higher (no external libraries needed — uses only the
  built-in `threading`, `time`, and `collections` modules)

## How to Run

Open a terminal in this folder and run:

```
python3 sync_demo.py
python3 scheduler.py
```

(On Windows, use `python` instead of `python3` if that's how Python is
registered on your PATH.)

## What Each Program Demonstrates

### sync_demo.py
1. **Race condition** — 5 threads increment a shared bank balance
   100,000 times total with no locking. A small forced delay between the
   read and write steps simulates realistic thread interleaving, so the
   final balance comes out lower than expected (updates are lost).
2. **Synchronization fix** — the same test is repeated using a
   `threading.Lock()` around the critical section. The final balance is
   now always correct.
3. **Deadlock prevention** — two threads each need two locks (A and B).
   If they acquired the locks in opposite order, they could deadlock
   (this scenario is left in the code, commented out, since it hangs on
   purpose). The program instead demonstrates the fix: both threads
   acquire locks in the same fixed order (A before B), which makes a
   circular wait — and therefore deadlock — impossible.

### scheduler.py
Simulates the round-robin scheduling algorithm with a configurable time
quantum (default: 4). Given a set of processes with arrival and burst
times, it:
- Allocates CPU time in fixed slices, cycling through the ready queue
- Prints a Gantt chart showing the exact execution order and timing
- Calculates completion time, turnaround time, and waiting time per
  process, plus system-wide averages

You can change the `processes` list and `QUANTUM` value at the bottom of
`scheduler.py` to test different scenarios.

## Design Decisions (for your 500–750 word writeup)

Points you can expand on in your own words:
- **Why a Lock (mutex) rather than a Semaphore?** A binary mutex is the
  simplest correct tool for protecting a single shared variable accessed
  by multiple threads — a semaphore is more appropriate when limiting
  access to a *pool* of N interchangeable resources, which isn't the case
  here.
- **Why deliberately force the race condition with a sleep?** Python's
  Global Interpreter Lock (GIL) can make simple operations fast enough
  that races don't reliably appear by chance. Inserting a short delay
  between the read and write steps forces the scheduler to interleave
  threads, reliably reproducing the same class of bug that occurs
  naturally in lower-level languages without a GIL (e.g. C/C++).
- **Why lock ordering for deadlock prevention?** It's one of the simplest
  and most widely used deadlock-prevention strategies: if every thread in
  the system acquires shared locks in the same global order, a circular
  wait condition (a requirement for deadlock) can never form.
- **Why round-robin?** It's a preemptive scheduling algorithm designed
  for fairness in time-sharing systems — no process can monopolize the
  CPU, since each gets bounded fixed the time slice before returning to
  the back of the queue.

## Screenshots
Take a screenshot of both terminal outputs after running the programs and
place them in the `screenshots/` folder, named e.g.
`sync_demo_output.png` and `scheduler_output.png`.
