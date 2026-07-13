# Task 2: Memory Management Simulation

## Files
- `paging_simulator.py` — Paging simulator implementing FIFO and LRU
  page replacement
- `frame_scaling_experiment.py` — Bonus script comparing FIFO vs LRU
  across multiple frame counts (2–6), useful evidence for your report
- `fault_comparison.png` — Auto-generated bar chart (from
  `paging_simulator.py`)
- `faults_vs_frames.png` — Auto-generated line chart (from
  `frame_scaling_experiment.py`)

## Requirements
- Python 3.8+
- `matplotlib` for the comparison chart:
  ```
  pip install matplotlib
  ```
  (The script still runs and prints full results without matplotlib —
  it just skips the chart and prints a note.)

## How to Run

```
python3 paging_simulator.py
python3 frame_scaling_experiment.py
```

This will:
1. Run the FIFO simulation, printing a step-by-step log of every page
   access (hit or fault) and the resulting frame contents
2. Run the LRU simulation the same way
3. Print a summary table comparing hit/fault counts and ratios
4. Save a bar chart (`fault_comparison.png`) visually comparing the two

## How It Works

- **Frames**: physical memory is modelled as a fixed-size list
  (`NUM_FRAMES = 3` by default) holding the page numbers currently
  resident in memory.
- **FIFO**: uses a queue to track the order pages entered memory. On a
  fault with no free frames, the oldest page (front of the queue) is
  evicted — regardless of how recently it was actually used.
- **LRU**: tracks the step number each page was last accessed. On a
  fault with no free frames, the page with the oldest "last used" time
  is evicted.
- **Reference string**: `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0,
  1, 7, 0, 1]` — a classic OS-textbook example, chosen deliberately
  because it demonstrates a clear performance difference between the two
  algorithms (LRU: 60% fault ratio vs FIFO: 75% fault ratio, with 3
  frames).

You can change `NUM_FRAMES` or `reference_string` at the bottom of the
script to test other scenarios — try increasing the number of frames and
observe how both algorithms' fault ratios drop.

## Notes for Your Analysis Report (500–750 words)

Use the printed results as your evidence base. Points you can develop in
your own words:

- **Why LRU generally outperforms FIFO**: LRU evicts based on *actual
  usage recency*, so a page that's still being reused frequently (like
  pages 0 and 1 in this reference string) tends to stay in memory. FIFO
  evicts purely by *arrival order*, so it can evict a page that's still
  in active use simply because it's been resident the longest.
- **But it's not universal** — running `frame_scaling_experiment.py`
  shows FIFO actually *outperforms* LRU at 2 frames (15 vs 17 faults),
  LRU wins clearly at 3–5 frames, and they tie at 6 frames. This is
  genuinely useful evidence for your report: it shows that LRU's
  advantage depends on frame count and workload, not that it's always
  strictly better — a more accurate and defensible claim than a blanket
  "LRU is better."
- **Belady's Anomaly**: a well-known property of FIFO specifically is
  that its fault count can *increase* even when given *more* frames,
  which is counter-intuitive. LRU does not suffer from this. Worth
  mentioning as a known theoretical weakness of FIFO, even though it's
  not directly demonstrated by the data above.
- **Trade-offs**: LRU is generally the better predictor of real usage
  patterns but is more expensive to implement in a real OS, since exact
  LRU requires tracking access history for every page. Real systems
  often approximate it using "reference bits" or "clock" algorithms
  instead, because exact LRU has non-trivial overhead.
- Use the table/chart produced by `frame_scaling_experiment.py` directly
  as a figure in your report — it's stronger evidence than a single data
  point.
