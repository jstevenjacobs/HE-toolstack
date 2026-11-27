# GROK — Round-07 re-pin-7 reply (protocol rev-8, pin `a6953989fe74ba256dae90215ac41208d570a32d`)

Pin reviewed: a6953989fe74ba256dae90215ac41208d570a32d

Sources: protocol §3.8; runner (budget / PENDING / UNPROVEN / corrupt-state paths); test_broker_p0.py check anchors through P0-20. Paper-only.

## Q1 — Does ACCEPT stand at a695398?

ACCEPT stands at this pin.

§3.8 is byte-identical to the wording accepted since rev-3/rev-4 (fetched at this pin). Architecture, threat bound, and "no second machine / no TPM / no attestation against the owner" are unchanged.

Rev-8 is again implementation reliability inside that bound. Spot-checks against the claim→evidence surface:

| Area | Anchors seen at pin |
|---|---|
| Spawn / decode separation; lossy UTF-8 recorded as executed, not UNPROVEN | P0-17d, P0-17d2, P0-17d3 |
| Budget survives fresh ids; history + spawn_succeeded:false exclusion | P0-15, P0-20b, P0-20c |
| Corrupt budget / ledger fail-closed | P0-19a/b, P0-20d/e/f |
| Plan absent / unsigned / bad shape ⇒ PENDING, not terminal | P0-16a/b, P0-9d, P0-1a/b, P0-2* |
| Collision before lifecycle branches | P0-13a–d |
| §3.8 identity | in-generator live diff claimed; text match confirmed by fetch |

No architectural expansion. Residual remains exactly §3.8.

The honest disclosure that an earlier §3.8 "vacuous awk" check was corrected (row 20) is process-positive, not a protocol defect.

## Q2 — Standing pre-send gate

Yes — meets the re-pin-5 process bar.

Required properties, all present in this prompt:
- Claims cite path:symbol or test-id with pin-local anchors.
- Table is produced by an in-tree fail-loud generator (not draft memory).
- Gaps are declared (e.g. instrumented exceptions in the suite docstring; revoke script unchanged since rev-7 with clean diff).
- Prior false prompt claims are walked back on the record (ledger / changelog), not papered over.

That is sufficient process hygiene for this seat. No further process remedy is required to accept rev-8's technical content at this pin.

## Vote

**ACCEPT**

2/2 voting ACCEPT at this pin ⇒ Wave 0 authorized to begin only (§9): owner runs the cutover sequence, §3.6 multi-leg test (including public test-pack fetch + digest verification), C1/C2 host prep via broker, zero destructive ops.

Wave-0 rulings still need their own evidence pack and 2/2 validation before they bind (§2a). R-4/R-5/R-7 remain recorded exceptions until Wave-3 live evidence. DESIGN-REVIEW §10 HARD STOP untouched. No authorization beyond Wave 0 start.
