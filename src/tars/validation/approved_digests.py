"""Approval anchors for validation inputs (review M2-T6 F32, F33; DR-0019 B).

The files that decide whether the Proof passes -- the threshold files and the GMAT M2
reference manifest -- are authenticated against sha256 digests pinned here, in
reviewed source. Tampering with a file (inflated finite limits, a rewritten manifest
history) is rejected; changing one legitimately (the T7 threshold DR, a regenerated
GMAT reference) needs a reviewed commit that updates the digest here. Bypassing the
pin requires editing validator source, which DR-0019 B places under code review.

Update procedure: change the file, review it, then set its new digest below in the
same reviewed change (``shasum -a 256 <file>``).
"""

APPROVED_THRESHOLD_SHA256 = {
    # proof/thresholds/m1.json: approved by the Tech Lead 2026-10-05 (DR-0008, DR-0009).
    "m1": "446e75ee8d5129a346263b5b06f873e0aed74c33fd756564e43423bbd16fdb3d",
    # proof/thresholds/m2.json: PROVISIONAL (T5/T6); the pin authenticates the reviewed
    # content, it does not approve the values (T7 threshold DR).
    "m2": "7e4883b60df00f48f3713609068ce4387be2c1b3f6d33cf2f7924a004771652b",
}

# toolbox/references/gmat/m2/APPROVED_DIGESTS.json: reference digests and the
# hash-chained history of all four generations (reviewed in M2-T6-review-01).
APPROVED_GMAT_M2_MANIFEST_SHA256 = (
    "f8d6bd788eb1e305af72cad2b821b4b85b2c65ab64410059ca43299eee5ce585"
)
