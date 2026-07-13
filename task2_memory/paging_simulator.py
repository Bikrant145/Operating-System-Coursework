"""
Task 2: Memory Management Simulation
ST5004CEM Operating Systems and Security

Simulates virtual memory paging with a configurable number of physical
frames and page size. Implements two page replacement algorithms:
    - FIFO (First-In-First-Out)
    - LRU  (Least Recently Used)

For a given reference string (sequence of page numbers requested by a
process), the simulator tracks page hits/faults, shows frame contents
after every access, and reports the hit/miss ratio for each algorithm so
they can be compared directly.
"""

from collections import deque


class PagingSimulator:
    def __init__(self, num_frames, page_size_kb=4):
        """
        num_frames   : number of physical memory frames available
        page_size_kb : size of each page in KB (for reporting only -
                       does not affect the replacement logic)
        """
        self.num_frames = num_frames
        self.page_size_kb = page_size_kb

    # -----------------------------------------------------------------
    # FIFO PAGE REPLACEMENT
    # -----------------------------------------------------------------
    def run_fifo(self, reference_string, verbose=True):
        """
        Replaces the page that has been in memory the LONGEST,
        regardless of how recently it was used.
        """
        frames = []                     # current pages in memory (ordered)
        fifo_queue = deque()            # tracks arrival order for eviction
        hits = 0
        faults = 0
        history = []                    # for logging / visualization

        for step, page in enumerate(reference_string, start=1):
            if page in frames:
                hits += 1
                event = "HIT"
            else:
                faults += 1
                event = "FAULT"
                if len(frames) < self.num_frames:
                    frames.append(page)
                    fifo_queue.append(page)
                else:
                    evicted = fifo_queue.popleft()   # oldest page
                    frames[frames.index(evicted)] = page
                    fifo_queue.append(page)

            history.append((step, page, event, list(frames)))
            if verbose:
                print(f"Step {step:>3} | Access page {page:>3} | {event:<5} | "
                      f"Frames: {frames}")

        return {
            "algorithm": "FIFO",
            "hits": hits,
            "faults": faults,
            "total": len(reference_string),
            "hit_ratio": hits / len(reference_string),
            "fault_ratio": faults / len(reference_string),
            "history": history,
        }

    # -----------------------------------------------------------------
    # LRU PAGE REPLACEMENT
    # -----------------------------------------------------------------
    def run_lru(self, reference_string, verbose=True):
        """
        Replaces the page that has not been used for the LONGEST time
        (i.e. was accessed least recently).
        """
        frames = []                      # current pages in memory
        recency = {}                     # page -> last-used step index
        hits = 0
        faults = 0
        history = []

        for step, page in enumerate(reference_string, start=1):
            if page in frames:
                hits += 1
                event = "HIT"
            else:
                faults += 1
                event = "FAULT"
                if len(frames) < self.num_frames:
                    frames.append(page)
                else:
                    # find the page with the smallest (oldest) last-used step
                    lru_page = min(frames, key=lambda p: recency[p])
                    frames[frames.index(lru_page)] = page

            recency[page] = step  # mark this page as most recently used
            history.append((step, page, event, list(frames)))
            if verbose:
                print(f"Step {step:>3} | Access page {page:>3} | {event:<5} | "
                      f"Frames: {frames}")

        return {
            "algorithm": "LRU",
            "hits": hits,
            "faults": faults,
            "total": len(reference_string),
            "hit_ratio": hits / len(reference_string),
            "fault_ratio": faults / len(reference_string),
            "history": history,
        }


def print_summary(result):
    print(f"\n--- {result['algorithm']} Summary ---")
    print(f"Total accesses : {result['total']}")
    print(f"Page hits      : {result['hits']}")
    print(f"Page faults    : {result['faults']}")
    print(f"Hit ratio      : {result['hit_ratio']:.2%}")
    print(f"Fault ratio    : {result['fault_ratio']:.2%}")


def print_comparison_table(results):
    print("\n" + "=" * 50)
    print("ALGORITHM COMPARISON")
    print("=" * 50)
    print(f"{'Algorithm':<10}{'Hits':<8}{'Faults':<8}{'Hit Ratio':<12}{'Fault Ratio':<12}")
    for r in results:
        print(f"{r['algorithm']:<10}{r['hits']:<8}{r['faults']:<8}"
              f"{r['hit_ratio']:<12.2%}{r['fault_ratio']:<12.2%}")

    best = min(results, key=lambda r: r['faults'])
    print(f"\nBest performer for this reference string: {best['algorithm']} "
          f"({best['faults']} faults vs "
          f"{[r['faults'] for r in results if r != best]})")


def plot_comparison(results, filename="fault_comparison.png"):
    """
    Generates a bar chart comparing page faults between algorithms.
    Requires matplotlib: pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[Skipping chart: matplotlib not installed. "
              "Run 'pip install matplotlib' to enable this.]")
        return

    algorithms = [r["algorithm"] for r in results]
    faults = [r["faults"] for r in results]
    hits = [r["hits"] for r in results]

    x = range(len(algorithms))
    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([i - width / 2 for i in x], hits, width, label="Hits", color="#4CAF50")
    ax.bar([i + width / 2 for i in x], faults, width, label="Faults", color="#E57373")

    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Count")
    ax.set_title("Page Hits vs Faults: FIFO vs LRU")
    ax.set_xticks(list(x))
    ax.set_xticklabels(algorithms)
    ax.legend()
    plt.tight_layout()
    plt.savefig(filename)
    print(f"\nChart saved to '{filename}'")


if __name__ == "__main__":
    NUM_FRAMES = 3

    # This is a classic, widely-used OS-textbook reference string, chosen
    # because it clearly shows LRU outperforming FIFO on this workload
    # (LRU better captures the pages that keep getting reused, such as 0
    # and 1, while FIFO evicts them purely based on age).
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]

    print("=" * 70)
    print(f"MEMORY PAGING SIMULATION  (Frames = {NUM_FRAMES})")
    print(f"Reference string: {reference_string}")
    print("=" * 70)

    sim = PagingSimulator(num_frames=NUM_FRAMES)

    print("\n### FIFO Page Replacement ###")
    fifo_result = sim.run_fifo(reference_string)
    print_summary(fifo_result)

    print("\n### LRU Page Replacement ###")
    lru_result = sim.run_lru(reference_string)
    print_summary(lru_result)

    print_comparison_table([fifo_result, lru_result])
    plot_comparison([fifo_result, lru_result])
