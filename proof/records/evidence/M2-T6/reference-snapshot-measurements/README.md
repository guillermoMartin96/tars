# Reference snapshot deviation measurements (VAL-0015, DR-0021 condition 4)

Verify-mode deviations against baseline 1, with unlimited tolerances (`reference_snapshot.py
measure-deviation`). Each file gives the largest |runtime - approved| by class, by entrypoint,
together with the environment.

- `reference-host-deviation.json`: the reference host (macOS x86_64, i9-9880H), measured
  against the identical measurement recording. Every class is 0.
- `ci2-*`, `m<run id>-*`: GitHub Actions workflow `reference-snapshot-measure`, tags
  `refsnap-measure-2` to `-5`. Runs 38291386470, 38292229310, 38292231479 and 38292235152.
- `b2-<run id>-*`: the same against baseline 2 (tags `refsnap-measure-6` to `-9`), runs 38320405875, 38320407537, 38320409961 and 38320411392.
- `b3-<run id>-*`: the same against baseline 3 (tags `refsnap-measure-10` to `-13`), runs 38450053216, 38450056198, 38450061306 and 38450063228. The macOS job of 38450061306 was cancelled before any step ran (no runner was assigned), so 7 files.
