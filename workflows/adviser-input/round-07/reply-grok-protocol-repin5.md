# GROK — Round-07 re-pin-5 verdict (protocol rev-6)

Adviser: Grok (voting member)
Pin reviewed: 3f3b04a3ea0a83afd4964e1a17287467a0121988
Received: 2026-11-26
Verdict: **ACCEPT** (stands) — 1/2 votes pending ChatGPT
Note: rendered with the adviser's UI link-cards stripped; text otherwise verbatim.

---

Pin reviewed: 3f3b04a3ea0a83afd4964e1a17287467a0121988

Sources: protocol §3.8; scripts/m0-broker-runner.py (durable_write); scripts/m0-broker-revoke-keys.sh; scripts/qa/test_broker_p0.py (P0-10…P0-17 bodies). Paper-only.

## Q1 — Does ACCEPT stand?

ACCEPT stands at this pin.

§3.8 is byte-identical to the wording accepted since rev-3/rev-4 (slice-fetched at this pin; matches 8509096 / 1ce2b3c). Architecture, threat bound, and "no second machine / no TPM / no attestation against the owner" are unchanged.

Rev-6 changes are implementation reliability inside that bound. Spot-checked claim→code→test mapping:

| Claim | Code locus | Test body present |
|---|---|---|
| fsync file + parent dir | durable_write: os.fsync(fh) then os.fsync(dfd) after os.replace | P0-12a, P0-12b |
| Inventory-wide verify + strict recovery grammar | m0-broker-revoke-keys.sh verify_inventory; only `local-console` \| `keep:<SHA256:…>` | P0-11a/b/b2/c/d |
| ID collision → explicit refusal, no re-exec | runner disposition path | P0-13a, P0-13b |
| Pre-spawn artifact digests | plan artifacts check before spawn | P0-14a, P0-14b |
| max_runs use-budget survives fresh ids | plan+argv-keyed budget | P0-15 |
| Plan absent ⇒ PENDING, not blacklist | no disposition until signed plan | P0-16a, P0-16b |
| Spawn OSError ⇒ definite record, not UNPROVEN | spawn_succeeded: false | P0-17a, P0-17b |
| --once exactly one cycle, exit 0 | runner flag | P0-10 (strengthened) |

Docstring scenario list and test bodies are one-to-one at this pin (the re-pin-4 defect is closed). No architectural expansion; residual remains exactly §3.8.

## Q2 — Process view on repeated prompt-accuracy failures

Two false prompt claims in one round (rev-4 `--once`; rev-5 phantom P0-12…17 / P0-11 inventory verification) is a **process defect, not a code defect**. Recorded corrections in changelog + ledger are necessary but not sufficient as a standing control.

Recommendation (non-blocking for this vote): for future re-pin prompts, adopt a mechanical pre-send rule:

1. Every concrete claim about runner/script/test behavior cites `path:symbol` or test-id **and a line/section anchor** in the committed tree at the declared pin.
2. Claims of the form "P0-N exists / passes" require that the **test function body exists in the pin's** `test_broker_p0.py` (not only the module docstring).
3. A short **claim→evidence table in the prompt itself, generated from the pin**, not from memory of a prior draft.

This is process hygiene for the council's evidence surface. It does not change the ACCEPT on rev-6's technical content at this pin, where the cited tests are present and mapped.

## Vote

**ACCEPT**

2/2 ACCEPT at this pin ⇒ Wave 0 authorized to begin only (§9): owner runs the cutover sequence, §3.6 multi-leg test (including public test-pack fetch + digest verification), C1/C2 host prep via broker, zero destructive ops.

Wave-0 rulings still need their own evidence pack and 2/2 validation before they bind (§2a). R-4/R-5/R-7 remain recorded exceptions until Wave-3 live evidence. DESIGN-REVIEW §10 HARD STOP untouched. No authorization beyond Wave 0 start.
