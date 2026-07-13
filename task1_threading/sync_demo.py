"""
Task 1 - Part A: Process/Thread Synchronization Demo
ST5004CEM Operating Systems and Security

This program demonstrates:
1. Multiple threads performing concurrent operations (5 threads)
2. A race condition (no synchronization) -> incorrect results
3. Proper synchronization using a Lock (mutex) -> correct results
4. A deadlock scenario (two locks, two threads) and its prevention
   using consistent lock ordering
"""

import threading
import time
import random

# ---------------------------------------------------------------------------
# SHARED RESOURCE
# ---------------------------------------------------------------------------
# A simple bank account balance shared across multiple worker threads.
# This is a classic example of a "critical section" - a piece of shared
# state that must not be modified by more than one thread at a time.

NUM_THREADS = 5          # minimum requirement is 3, we use 5 to make races obvious
OPERATIONS_PER_THREAD = 2000
DEPOSIT_AMOUNT = 1

# Python's Global Interpreter Lock (GIL) makes a *bare* increment fast enough
# that a race rarely shows up by chance. To reliably DEMONSTRATE the race
# condition (the same way it would naturally occur in C/C++ or Java without
# a GIL), we insert a tiny sleep between the read and the write below. This
# forces the OS scheduler to switch to another thread mid-operation, which
# is exactly the kind of interleaving that causes real race conditions.
CONTEXT_SWITCH_DELAY = 0.0001


# ---------------------------------------------------------------------------
# PART 1: RACE CONDITION (NO LOCK)
# ---------------------------------------------------------------------------
class UnsafeAccount:
    def __init__(self):
        self.balance = 0

    def deposit(self):
        # This looks like a single operation, but it is actually THREE steps:
        #   1. read self.balance
        #   2. add 1 to it
        #   3. write it back
        # If two threads interleave between steps 1 and 3, one thread's
        # update can be silently lost. This is the race condition.
        current = self.balance
        time.sleep(CONTEXT_SWITCH_DELAY)   # forces a thread interleaving window
        current += DEPOSIT_AMOUNT
        self.balance = current


def worker_unsafe(account):
    for _ in range(OPERATIONS_PER_THREAD):
        account.deposit()


def run_race_condition_demo():
    print("=" * 70)
    print("PART 1: DEMONSTRATING A RACE CONDITION (no synchronization)")
    print("=" * 70)

    account = UnsafeAccount()
    threads = []

    start = time.time()
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker_unsafe, args=(account,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    elapsed = time.time() - start

    expected = NUM_THREADS * OPERATIONS_PER_THREAD * DEPOSIT_AMOUNT
    print(f"Threads used        : {NUM_THREADS}")
    print(f"Expected balance    : {expected}")
    print(f"Actual balance      : {account.balance}")
    print(f"Lost updates        : {expected - account.balance}")
    print(f"Time taken          : {elapsed:.3f}s")
    if account.balance != expected:
        print("RESULT: Race condition confirmed - final balance is WRONG.\n")
    else:
        print("RESULT: No race observed this run (can still happen "
              "non-deterministically) - try increasing OPERATIONS_PER_THREAD.\n")


# ---------------------------------------------------------------------------
# PART 2: FIXING THE RACE CONDITION WITH A LOCK (MUTEX)
# ---------------------------------------------------------------------------
class SafeAccount:
    def __init__(self):
        self.balance = 0
        self.lock = threading.Lock()   # the mutex protecting self.balance

    def deposit(self):
        # Only one thread can hold self.lock at a time. Any other thread
        # calling deposit() will block until the lock is released, which
        # makes the read-modify-write sequence atomic with respect to
        # other threads.
        with self.lock:
            current = self.balance
            current += DEPOSIT_AMOUNT
            self.balance = current


def worker_safe(account):
    for _ in range(OPERATIONS_PER_THREAD):
        account.deposit()


def run_synchronized_demo():
    print("=" * 70)
    print("PART 2: FIXING THE RACE CONDITION WITH A LOCK")
    print("=" * 70)

    account = SafeAccount()
    threads = []

    start = time.time()
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker_safe, args=(account,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    elapsed = time.time() - start

    expected = NUM_THREADS * OPERATIONS_PER_THREAD * DEPOSIT_AMOUNT
    print(f"Threads used        : {NUM_THREADS}")
    print(f"Expected balance    : {expected}")
    print(f"Actual balance      : {account.balance}")
    print(f"Time taken          : {elapsed:.3f}s")
    assert account.balance == expected, "Synchronization failed!"
    print("RESULT: Balance is CORRECT - lock successfully prevented the race.\n")


# ---------------------------------------------------------------------------
# PART 3: DEADLOCK DEMONSTRATION AND PREVENTION
# ---------------------------------------------------------------------------
# A deadlock happens when Thread 1 holds Lock A and waits for Lock B,
# while Thread 2 holds Lock B and waits for Lock A. Neither can proceed.
#
# Prevention strategy used here: LOCK ORDERING.
# Every thread must always acquire the locks in the SAME global order
# (lock_a before lock_b), regardless of which "task" it is performing.
# This makes a circular wait impossible.

lock_a = threading.Lock()
lock_b = threading.Lock()


def deadlock_prone_worker_1():
    # Acquires A then B
    with lock_a:
        time.sleep(0.1)  # gives the other thread a chance to grab lock_b
        with lock_b:
            pass


def deadlock_prone_worker_2():
    # Acquires B then A  -> OPPOSITE order to worker_1 -> potential deadlock
    with lock_b:
        time.sleep(0.1)
        with lock_a:
            pass


def safe_worker_1():
    # Both workers now acquire in the SAME order: A then B
    with lock_a:
        time.sleep(0.05)
        with lock_b:
            pass


def safe_worker_2():
    with lock_a:
        time.sleep(0.05)
        with lock_b:
            pass


def run_deadlock_demo():
    print("=" * 70)
    print("PART 3: DEADLOCK PREVENTION (consistent lock ordering)")
    print("=" * 70)

    print("Running SAFE version where both threads acquire locks in the "
          "same order (A then B). This should complete immediately "
          "without hanging.")

    t1 = threading.Thread(target=safe_worker_1)
    t2 = threading.Thread(target=safe_worker_2)

    start = time.time()
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    elapsed = time.time() - start

    if t1.is_alive() or t2.is_alive():
        print("RESULT: Threads are still stuck - deadlock occurred!\n")
    else:
        print(f"RESULT: Both threads completed safely in {elapsed:.3f}s. "
              "No deadlock, because lock ordering was consistent.\n")

    print("NOTE: If deadlock_prone_worker_1() and deadlock_prone_worker_2()\n"
          "were run together instead (opposite lock order), the program\n"
          "would hang forever. That version is left in the code, commented\n"
          "out from execution, to avoid freezing the demo - see below.\n")

    # Uncomment the following 5 lines to WITNESS a real deadlock.
    # WARNING: this will hang forever and you must kill the program (Ctrl+C).
    #
    # t3 = threading.Thread(target=deadlock_prone_worker_1)
    # t4 = threading.Thread(target=deadlock_prone_worker_2)
    # t3.start(); t4.start()
    # t3.join(); t4.join()
    # print("This line will never print if deadlock occurs.")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_race_condition_demo()
    run_synchronized_demo()
    run_deadlock_demo()
    print("All demonstrations complete.")
