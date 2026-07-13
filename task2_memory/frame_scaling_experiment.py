"""
Task 2 (bonus/innovation): Compare FIFO vs LRU across multiple frame counts.

Running the same reference string with different numbers of physical
frames shows how each algorithm's performance scales with more memory,
and gives stronger, multi-data-point evidence for the analysis report
than a single run.
"""

from paging_simulator import PagingSimulator

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


REFERENCE_STRING = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
FRAME_COUNTS = [2, 3, 4, 5, 6]


def main():
    fifo_faults = []
    lru_faults = []

    print("=" * 60)
    print("FIFO vs LRU across increasing frame counts")
    print("=" * 60)
    print(f"{'Frames':<10}{'FIFO Faults':<15}{'LRU Faults':<15}")

    for n in FRAME_COUNTS:
        sim = PagingSimulator(num_frames=n)
        f = sim.run_fifo(REFERENCE_STRING, verbose=False)
        l = sim.run_lru(REFERENCE_STRING, verbose=False)
        fifo_faults.append(f["faults"])
        lru_faults.append(l["faults"])
        print(f"{n:<10}{f['faults']:<15}{l['faults']:<15}")

    if HAS_MPL:
        plt.figure(figsize=(6, 4))
        plt.plot(FRAME_COUNTS, fifo_faults, marker="o", label="FIFO")
        plt.plot(FRAME_COUNTS, lru_faults, marker="o", label="LRU")
        plt.xlabel("Number of Frames")
        plt.ylabel("Page Faults")
        plt.title("Page Faults vs Frame Count")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("faults_vs_frames.png")
        print("\nChart saved to 'faults_vs_frames.png'")
    else:
        print("\n[Install matplotlib to generate a chart: pip install matplotlib]")


if __name__ == "__main__":
    main()
