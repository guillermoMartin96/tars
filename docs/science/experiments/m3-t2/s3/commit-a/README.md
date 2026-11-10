# M3 T2 S3 commit-A record

Phase A of the S3 sequence (proposal v4 section 15.1; PC-7(S3) issued 2026-11-10T22:29:49Z,
`~/tars-evidence/S3-PC7-issuance-v1/`, manifest `c504eb8a188beff020f2399ccf6c1257904fde8c7906d1e7d97103b58c62368d`).

- `generate_listing.py`: runs the committed generator on the twin's own parsed rows and writes
  `tests/s3_dl4_points.txt` and `listing-generation-record.json`.
- `listing-generation-record.json`: listing sha256 `01d88386a41738f4c595afdd3e231cf6be8784513e980208834fd06e54355919`,
  3 758 points (3 764 before de-duplication; the 6 known duplicates; no random collision), the
  generator and twin identities, and the r2 section 7.1 environment record of the generating
  process (S2 ENV node, D-S3-04 (a)).

The listing is exp-free and libm-independent; S3-T-18 asserts byte-identical regeneration on
every platform. This record holds no density value; densities are UNVERIFIED ABOVE 1000 KM.
The A-red and A-green run records are external (`~/tars-evidence/S3-implementation-v1/records/`).
