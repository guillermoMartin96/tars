# M3 T2 S1: OD-7 record of I-30 §4 (Scientific and Decision Boundaries)

- **Status:** prepared under owner instruction I-56 (2026-10-31), recorded append-only. **OD-7 is not
  closed by this record.** It stays OPEN until the owner accepts this record and formally closes OD-7.
  Until then the S1 review prompt stays BLOCKED (I-40 §3).
- **Purpose:** I-40 §3 (OD-7) requires a docs commit that records I-30 §4 immutably, so that the S1
  review prompt can quote "I-30 §4 as recorded (OD-7)" (I-40 §14). Revision 2 §10 requires the T2
  review prompt to quote I-30 §4 verbatim. Until this record, the §4 text was in no repository file.
- **Scope:** documentation only. No production code, test, CI, dependency, scenario or proof file is
  changed.
- **Not edited:** `M3-T2-S1-authorization.md` (I-40) and `M3-T2-implementation-authorization-packet.md`
  (revision 2). The OD-7 alternative "amend r2 §10's quote list" is not used.
- **Preservation statement:** this record preserves the original I-30 §4 scientific and decision
  boundaries without modifying them. It does not paraphrase, reinterpret, strengthen or weaken any of
  them. It adds no acceptance criterion, decides no open item and changes the state of nothing that §4
  lists.

## 1. The original instruction

- **Identifier:** I-30, "I-30 — T2 Owner-Decision Reconciliation Acceptance and Merge Authorization".
- **Date:** 2026-10-26. Owner message timestamp `2026-10-26T15:48:10.541Z`.
- **Sections of I-30:** §1 Acceptance; §2 Pre-Merge Verification; §3 Merge Authorization; §4 Scientific
  and Decision Boundaries; §5 Post-Merge Verification; §6 Next Phase — T2 Authorization Preparation;
  §7 Stop Condition. Only §4 is recorded here.

## 2. I-30 §4, verbatim

The lines between the opening and closing fence lines below are I-30 §4 exactly: UTF-8, LF line
endings, no tabs, no trailing spaces. The heading level is **not** changed. The fence lines are not
part of the text.

````text
## 4. Scientific and Decision Boundaries

Preserve the following state:

- P1–P5 and P7–P10: DECIDED.
- P6: NOT FULLY DECIDED.
- Geodetic-drag residual: ESCALATED.
- DR-0028 P6(b): OPEN.
- X-1: NOT AUTHORIZED.
- RM-3b: unmeasured T4 candidate.
- A-FP-2, A-LM-1, and A-LM-2: not independently justified.
- Accuracy checks dependent on unjustified assumptions: report-only.
- Q-GATE, DQ-1 through DQ-6, and floating-point policy: unchanged.

The unexplained 0.14–0.38 m geodetic-drag residual continues to block geodetic GMAT acceptance in T5, but does not independently block T2.

Do not turn an unresolved scientific assumption into an acceptance criterion by documentation alone.
````

The only non-ASCII character in §4 is U+2013 EN DASH (UTF-8 `E2 80 93`), in "P1–P5", "P7–P10" and
"0.14–0.38". The state list has nine unnumbered `- ` items.

## 3. Provenance

- **Source:** the Claude Code session transcript in which the owner issued I-30:
  - file `~/.claude/projects/-Users-guillermomartin--superset-worktrees-tars-hissing-cotton-972e4c7c/2dfecf9f-860c-4edf-b1cf-2d19f932f0a1.jsonl`;
  - session `2dfecf9f-860c-4edf-b1cf-2d19f932f0a1`, working directory
    `/Users/guillermomartin/.superset/worktrees/tars/hissing-cotton-972e4c7c`, branch
    `m3-t2-owner-decisions-972e4c7c`;
  - JSON Lines record at 0-based line index 2112: `type` `user`, `message.role` `user`, `uuid`
    `53106f59-6bf1-4cf6-9694-85d989b2e6c3`, timestamp `2026-10-26T15:48:10.541Z`;
  - `message.content` is a single JSON string. It holds the pasted I-30 text inside the harness's
    `<pasted_content id="7a36">` … `</pasted_content id="7a36">` wrapper lines.
- **Uniqueness:** that record is the only user record in the transcript that contains `# I-30`.
- **Extractions:**
  - the I-55 extract (`~/tars-evidence/I-55/od7_I30_transcript_extract.txt`) holds a 446-byte comment
    header, then the complete message text, then one LF;
  - under I-56 the message was re-extracted from the transcript with a new script, independent of the
    I-55 extraction code. The two agree byte for byte, and §4 occurs at the same offset in both.
- **This is not an owner-supplied copy.** The source is a local transcript file, which is mutable. The
  text has been checked against that transcript and by an independent review. It becomes the owner's
  confirmed text only when the owner accepts this record.

## 4. SHA-256 hashes and boundaries

All hashes are over the raw bytes named, with no normalization.

| # | Bytes hashed | Size (bytes) | SHA-256 |
|---|---|---|---|
| H1 | The whole transcript file, as read on 2026-10-31 under I-55 and again under I-56 | 8 055 476 | `66a1fa473fd69910bd79b817c02d00745845a8d06e9907bf31aab4b31f85b469` |
| H2 | The raw JSON line at index 2112, without its terminating LF | 5 961 | `adc4bf8907f16ed31c6d2942461db49deca3e556503f483171430f46354f8b15` |
| H3 | The complete original message: the decoded `message.content` string, UTF-8 encoded, including the wrapper lines (starts `LF LF <pasted_content id="7a36"> LF`, ends `</pasted_content id="7a36"> LF`) | 5 152 | `30b0c61f960d682a4d4596c082793cee9d49eed0f06888140473f47264650766` |
| H4 | The pasted I-30 text inside the wrapper: from `# I-30 —` through the LF after `**T2 implementation remains NOT AUTHORIZED.**` | 5 095 | `bf8b0bea23002c23e9ef1a8812adf7c66205d7ed57b7463c8b2923e2b9a6692d` |
| H5 | §4 as a span of H3: from the first byte of the line `## 4. Scientific and Decision Boundaries` (H3 offset 2202) up to, not including, the first byte of the line `## 5. Post-Merge Verification` (offset 2890). Ends with `alone.` LF LF | 688 | `14bdd5cca29b5b8e2f441ba21510ca6a0392175674c20f15e895a6b0756261dc` |
| H6 | **§4 as recorded in §2 above:** H5 without its final LF, the blank separator line before §5. Starts `## 4.`, ends `alone.` LF | 687 | `8060023068975505e7c64585d5b92eeb4188e4d872b546fb98f48597e04286a8` |

- H3 is the hash of the complete original message. H5 and H6 are hashes of the §4 bytes only.
- H6 equals the bytes of this file from the line after the opening fence line through the LF that
  ends the line before the closing fence line.
- H3 and H1 were also recorded under I-55 (`OD-7-analysis.md`, `od7_I30_transcript_extract.txt`); the
  I-56 values are identical.

## 5. OD-7 resolution evidence

- **Requirement (I-40 §3, "Required before the S1 review"):** "I-30 §4: confirm the transcript text
  verbatim, or supply the authoritative text, and authorize a docs commit that records it immutably.
  Alternatively, amend r2 §10's quote list. Until then the S1 review prompt is BLOCKED".
- **Path taken:** the first option, the transcript text verbatim. I-56 authorizes this docs record. No
  owner-supplied text exists, and r2 §10 is not amended.
- **Evidence** (implementer evidence directory `~/tars-evidence/I-56/`, outside the repository):
  - the independent re-extraction and its byte comparison with the I-55 extract;
  - the hashes H1–H6 above;
  - an independent Codex review of this record against the transcript, I-40 and revision 2.
- **What remains for the owner:**
  - accept this record, which confirms the transcript text as I-30 §4;
  - authorize the push of this commit;
  - formally close OD-7.
- **Until then:** OD-7 stays OPEN, the S1 review prompt stays BLOCKED and the independent S1 review is
  not authorized. This record grants no S1 acceptance and no merge.
