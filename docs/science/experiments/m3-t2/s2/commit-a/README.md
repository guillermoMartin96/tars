# S2 commit A: the frozen DL-4 listing (proposal v11 section 3.10)

Authorized by PC-7(S2), issued under owner instruction I-99 (proposal v11 sha256
`f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809`).

- `generate_listing.py`: the one-time generation run. It ran on the host, on top of K
  `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`, before `src/tars/sim/geodesy.py` existed. It
  ran the committed generator `tests/s2_dl4_point_sets.py` (exact self-checks, OT-6/OT-7),
  asserted the six DG-CUSP witness slots (OT-8) and wrote `tests/s2_dl4_points.txt`.
- `listing-generation-record.json`: the listing's sha256, counts and labels, the generator's
  sha256 and git blob, and the generation environment (RG-POL-5: `sys.version`,
  `platform.platform()`, `platform.machine()`, the `uv.lock` sha256 and the interpreter
  executable's sha256). G-17a reads the sha256 from this record (RG-POL-2; stop 10).

The frozen listing is the only gate input (RG-POL-1). It is never regenerated in place,
edited or substituted. A re-run of the committed generator is a comparison only
(G-17a's report, G-17b).

Listing: 22 665 entries; labels 22 601 `passes`, 64 `evolute_region`, 0 `origin`;
8 853 class X entries.
