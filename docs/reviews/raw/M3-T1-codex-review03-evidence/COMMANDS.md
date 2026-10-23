
- `git archive --format=tar --output=review_scratch/b1566ae.tar b1566ae src` → review_scratch/check_00.log
  - exit 0; elapsed 0.03 s

- `git archive --format=tar --output=review_scratch/97b69ef.tar 97b69ef src` → review_scratch/check_01.log
  - exit 0; elapsed 0.03 s

- `tar -xf review_scratch/b1566ae.tar -C <SNAP>/review_scratch/reviewed_src_b1566ae` → review_scratch/check_02.log
  - exit 0; elapsed 0.02 s

- `tar -xf review_scratch/97b69ef.tar -C <SNAP>/review_scratch/reviewed_src_97b69ef` → review_scratch/check_03.log
  - exit 0; elapsed 0.02 s

- `<SNAP>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_constants.py tests/test_zonal_j2.py` → review_scratch/check_04.log
  - exit 0; elapsed 5.07 s

- `<SNAP>/.venv/bin/python docs/science/experiments/m3-t1/t1_review02_correction_check.py review_scratch/reviewed_src_b1566ae/src review_scratch/review02.json` → review_scratch/check_05.log
  - exit 0; elapsed 4.23 s

- `<SNAP>/.venv/bin/python docs/science/experiments/m3-t1/t1_review01_correction_check.py review_scratch/reviewed_src_97b69ef/src review_scratch/review01.json` → review_scratch/check_06.log
  - exit 0; elapsed 1.60 s

- `<SNAP>/.venv/bin/python docs/science/experiments/m3-t1/t1_j2_informational.py review_scratch/informational.json` → review_scratch/check_07.log
  - exit 0; elapsed 32.93 s

- `<SNAP>/.venv/bin/python docs/science/experiments/m3-t1/t1_mutation_check.py review_scratch/mutation.json` → review_scratch/check_08.log
  - exit 0; elapsed 236.99 s

- `<SNAP>/.venv/bin/python docs/science/experiments/m3-t1/t1_review02_survivors.py review_scratch/survivors.json` → review_scratch/check_09.log
  - exit 0; elapsed 15.23 s

- `<SNAP>/.venv/bin/python -m pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review01.py docs/science/experiments/m3-t0/check_review02.py docs/science/experiments/m3-t0/check_review03.py docs/science/experiments/m3-t0/check_review04.py docs/science/experiments/m3-t0/check_review05.py docs/science/experiments/m3-t0/check_review06.py docs/science/experiments/m3-t0/check_review07.py docs/science/experiments/m3-t0/check_review08.py docs/science/experiments/m3-t0/check_review09.py` → review_scratch/check_10.log
  - exit 0; elapsed 157.50 s

- `<SNAP>/.venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json` → review_scratch/check_11.log
  - exit 0; elapsed 9.05 s

- `<SNAP>/.venv/bin/python toolbox/validators/cross_platform.py` → review_scratch/check_12.log
  - exit 0; elapsed 0.82 s

- `<SNAP>/.venv/bin/python toolbox/validators/determinism.py` → review_scratch/check_13.log
  - exit 0; elapsed 1.65 s

- `<SNAP>/.venv/bin/python toolbox/validators/determinism.py --scenario scenarios/m2_burn_to_depletion.json` → review_scratch/check_14.log
  - exit 0; elapsed 1.95 s

- `<SNAP>/.venv/bin/python toolbox/validators/determinism.py --scenario scenarios/m2_invalid_commands.json` → review_scratch/check_15.log
  - exit 0; elapsed 1.94 s

- `<SNAP>/.venv/bin/python toolbox/validators/determinism.py --scenario scenarios/m2_prograde_burn.json` → review_scratch/check_16.log
  - exit 0; elapsed 1.97 s

- `<SNAP>/.venv/bin/python toolbox/validators/determinism.py --scenario scenarios/m2_retrograde_burn.json` → review_scratch/check_17.log
  - exit 0; elapsed 1.97 s

- `<SNAP>/.venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json` → review_scratch/check_18.log
  - exit 0; elapsed 122.56 s

- `<SNAP>/.venv/bin/python toolbox/validators/m2_cross_platform.py collect --out review_scratch/m2_platform.json` → review_scratch/check_19.log
  - exit 0; elapsed 4.24 s

- `<SNAP>/.venv/bin/ruff check .` → review_scratch/check_20.log
  - exit 0; elapsed 0.73 s

- `<SNAP>/.venv/bin/ruff format --check .` → review_scratch/check_21.log
  - exit 0; elapsed 0.05 s

## Additional review commands

See `INSPECTION_COMMANDS.md` for the read-only command inventory and saved scratch-script invocations, including adversarial probes, record audits, all six own mutations, and interval certification. The batch subprocesses above all exited 0. The full-suite command is `.venv/bin/python -m pytest -q -p no:cacheprovider > review_scratch/full_pytest.log 2>&1`; its final result is appended when complete.

## Final results

- Full-suite command: exit 0; 1288 passed, 3 warnings in 1725.99s (0:28:45).
- `python review_scratch/finalize_review.py`: generated final review from retained draft after asserting successful full-suite summary, pinned HEAD and clean tracked tree. Saved final_state.json and refreshed result inventory.
- `git status --porcelain` and `git diff --stat`: empty throughout; no tracked files needed restoration.
- `git rev-parse 60648b9`: 60648b93385a9954194730006aeac29ea14875ad.
- `git diff --name-only b1566ae..HEAD -- src tests`: forces.py and test_zonal_j2.py only.
- `sed -n 861,870p review_scratch/collected_tests.log`: remaining long reference-snapshot rejection tests; no failures inferred from duration.
