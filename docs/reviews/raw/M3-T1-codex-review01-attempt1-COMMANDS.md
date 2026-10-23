# Command ledger — M3 T1 Review 01

Commands below were executed in the supplied snapshot directory, in order. Shell groups used semicolons/newlines; no pipeline failure was inferred from a later successful command. Key output is recorded rather than a byte-for-byte terminal transcript.

## 1. Snapshot inventory

```sh
pwd; git status --porcelain; git rev-parse HEAD; git branch -a; git remote -v; git show-ref
```

Key output: supplied snap directory; status empty; HEAD 97b69ef92e589ebd1b71016f49c4c9816d8c724b, detached; local main and origin/main 60648b93385a9954194730006aeac29ea14875ad; origin T1 tracking ref at HEAD; origin URL https://github.com/guillermoMartin96/tars.git. No live fetch performed.

## 2. Scope inventory

```sh
git diff --stat 60648b9..97b69ef; git diff 60648b9..97b69ef -- src proof toolbox scenarios .github uv.lock pyproject.toml; rg --files -g AGENTS.md -g '*review*' -g '*validator*' -g 'DR-002*' -g 'ADR-000*'
```

Key output: 15 changed files, 1539 insertions, 2 deletions. Scoped diff: constants.py +58 lines, forces.py +39 lines; no other scoped changes. File inventory listed review and decision documents. The diff was inspected only for precondition/scope checks; it was not a completed code review.

## 3. Environment and ancestry

```sh
mkdir -p review_scratch
uname -a
uname -m
.venv/bin/python -c 'import sys, platform, importlib.metadata as m; print(sys.version); print(platform.platform()); print(platform.processor()); print("packages:"); print("\n".join(sorted(f"{d.metadata[chr(78)+chr(97)+chr(109)+chr(101)]}=={d.version}" for d in m.distributions())))'
git log --format='%H %s' 60648b9..97b69ef
git diff --name-only 60648b9..97b69ef -- proof toolbox scenarios .github uv.lock pyproject.toml
git merge-base --is-ancestor 60648b93385a9954194730006aeac29ea14875ad 97b69ef92e589ebd1b71016f49c4c9816d8c724b
 git status --porcelain
 git diff --stat
```

Key output: Darwin 25.2.0 / macOS 26.2 / x86_64, processor string i386; Python 3.12.15 / Clang 22.1.3. Package inventory is reproduced in the report. Four T1 commits matched the supplied sequence. Protected-path name diff empty. Ancestry command successful. Status and working diff empty.

## 4. CPU identification and final pre-write state

```sh
sysctl -n hw.model machdep.cpu.brand_string
 git status --porcelain --untracked-files=all
 git diff --stat
```

Key output: sysctl denied (`Operation not permitted`). Both git commands empty. CPU model not established.

## 5. Review artifacts

A shell heredoc wrote `review_scratch/M3-T1-codex-review01.md` with the complete final review, and a second heredoc wrote this ledger. No tracked files were written. The full heredoc content is the content of these two files.

## 6. Artifact verification

```sh
git status --porcelain --untracked-files=all
git diff --stat
.venv/bin/python -c 'from pathlib import Path; p=Path("review_scratch/M3-T1-codex-review01.md"); print("Report bytes:",p.stat().st_size); print("Ledger exists:",Path("review_scratch/COMMANDS.md").is_file())'
```

Key output: git status and diff empty; report nonempty; ledger exists. No tests, validators or experiments executed. No result files inspected.
