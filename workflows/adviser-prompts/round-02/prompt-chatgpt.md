# Adviser prompt — R2a freeze-repair review (carry verbatim to ChatGPT)

Repo: https://github.com/jstevenjacobs/HE-toolstack · PR #13 (base `main`, head commit `4acfb7c29de5576fa52ec76b7f6c84782d873727`). All anchors are raw-file URLs pinned to that SHA — never follow `/tree/` or `/blob/` browse URLs.

**Read (raw):**
- PR body: read via the PR page (`https://github.com/jstevenjacobs/HE-toolstack/pull/13`) — it states scope and the explicit NOT-in-scope list.
- Repaired row + footer: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4acfb7c29de5576fa52ec76b7f6c84782d873727/docs/HE-TOOLSTACK-QA-REPORT.md` (Q22 row line 38; footer at end)
- Repair method + evidence: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4acfb7c29de5576fa52ec76b7f6c84782d873727/workflows/adviser-input/round-02/q22-repair-evidence.md`
- Post-repair gate log: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4acfb7c29de5576fa52ec76b7f6c84782d873727/workflows/adviser-input/round-02/gate-run-postfix.txt`
- TD §8.8 flock clause: search the TD for "Process-crash behavior": `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4acfb7c29de5576fa52ec76b7f6c84782d873727/docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md`
- Pre-repair damage (read-only baseline, main): `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4b0838c/docs/HE-TOOLSTACK-QA-REPORT.md` (compare line 38)

**Task — verdict on each, with reasons:**
1. Q22 reconstruction rule: header kept verbatim from the truncated row; completion reconstructed from the intact r2-era row at `3feb698` (only the sentence construction "are defined in REQ §4 **and** rowed in the §5 matrix" + PASS tail reused — the r2 T-20 wording was deliberately NOT reused because r3 reworded T-20/T-21 after the O_EXCL→flock replacement; main row is not a byte-prefix). Acceptable, or do you require a different reconstruction (e.g. re-derivation from REQ §4/§5 directly)?
2. Errata-without-version-bump: QA stays v2.3, TD v1.13, because the Q16 gate pins header versions and a bump cascades cross-doc sync. Is in-row `[DP-R2a …]` annotation sufficient auditability, or does your review standard require a bump + Q16 re-pin as a separate round?
3. TD §8.8 clause: verify the SIGKILL/container-kill fd-close claim (you previously confirmed flock semantics independently). Any wording risk?
4. Whole-package sweep for the same truncation class: the Q22 damage was authoring-time and survived 10+ commits. Spot-check 5-10 other QA/RR rows you consider load-bearing for M0-freeze for mid-sentence endings; list any hits.

Reply format: `APPROVE` / `APPROVE-WITH-CHANGES` / `REJECT` + numbered findings, each labeled blocker/major/minor, each citing the file+line or URL you actually read. Silence = no-reply, never consent.
