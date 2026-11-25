# Council prompt (round-06 re-pin) — FIX VERIFICATION — for ChatGPT and Grok

You are the council re-reviewing the round-06 runbook repairs. This is the re-pin after
your round-06 reviews at `5315c372`. Both of your replies are archived verbatim IN the
tree at this pin (URLs below) — use your own demands and the other member's as the
yardstick, not my summary.

**HARD STOP (TD §10):** paper-only review. No runtime claims, no deployment or
ticket-execution authorization. Quote the pinned tree verbatim; never quote memory of a
previous pin for a claim about this one.

- **Pin:** `b125d6659e9f23a373405622eea4269cdc2c9875` (head of `dp/round-06-runbook-repairs`, PR #16)
- **Increment:** `5315c372..b125d665` — docs only: TD §11.8 (R-4/R-5/R-7), §12.5 (RC-4), ADR A1, ledger.

**Raw URLs (no login; all at the pin):**
- TD: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/b125d6659e9f23a373405622eea4269cdc2c9875/docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md`
- ADR: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/b125d6659e9f23a373405622eea4269cdc2c9875/docs/HE-TOOLSTACK-ADR.md`
- Ledger: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/b125d6659e9f23a373405622eea4269cdc2c9875/workflows/ledger.md`
- Round-06 replies (yours, archived): `…/b125d6659e9f23a373405622eea4269cdc2c9875/workflows/adviser-input/round-06/reply-chatgpt-runbook-review.md` and `…/reply-grok-runbook-review.md`

**The nine claimed fixes** (row = what the fix is supposed to be; verify against the tree):
1. R-4 source selection scoped to `$ROOT/heat-data/` (was `$ROOT`-level, which also contains `repo/` and `drills/`).
2. R-4 step-(6) proof: `?versionId=` read-back REMOVED (contradicted §6.9.3); now manifest-select → re-upload exported payload → digest-compare.
3. R-4 body gained the replacement-volume provision/mount + copy + host **seed-script** sequence (the ledger gloss had claimed steps the body lacked).
4. R-4 body states the cold-session rule (T0.5) explicitly.
5. R-5: status probe relabeled liveness-only; adds one controlled `POST /v1/create_run` exercise (allowed digest, normal restrictions) + cancel/cleanup; `make test-smoke` explicitly disclaimed as this runbook's proof.
6. R-5: host docker check reclassified — docker engine = §2.6 host prerequisite, NOT the §11.9 class-X unit (backup timer).
7. R-7: data-loss fallback reversed — if archive destination unavailable, deletion is limited to the live-verified promoted tier; `work/` may not be deleted without its own archived+digest-verified copy (§9.2).
8. R-7: archive child dir `[E]`→`[P]`; live-MinIO head/get distinguished from the [P]/T-22 backup export; per-run archive layout + collision rule + post-move digest verification added; 95 % watermark qualified `[proposal]` (§11.6).
9. External corrections: ADR A1 `R-4/R-8` restore citation annotated superseded; RC-4 scope note (R-9 = daemon-restart class, not host-reboot drill); ledger DP-R6-rb gloss carries a rev-2 note stating the body was raised to match the gloss, not vice versa.

**Q1 — Per-fix ACCEPT/REOPEN (1–9).** For each: quote the exact corrected text at the pin and rule ACCEPT or REOPEN with reasoning. The yardstick is your round-06 demand text (it is in the tree).

**Q2 — New-defect hunt on the increment only.** The fixes added ~40 lines of operational prose. Hunt for: contradictions with D-16 / lifecycle classes / six-step shutdown / §6.9 / §9.2 / §9.4 / §11.5–§11.9; any command or threshold presented as live that is [proposal]; any internal mismatch between the three runbook bodies and the ledger gloss AT THIS PIN.

**Q3 — Status discipline.** Confirm nothing in the increment reads as closing the R-4/R-5/R-7 exceptions or the §9 annotation on paper. State plainly whether the gloss-vs-body reconciliation is now honest in both directions.

**Q4 — Final verdict on the round-06 drafts** (APPROVE / APPROVE-WITH-CHANGES / REJECT). Paper acceptance only: the exceptions close solely by M0 re-execution with evidence (T-11 class drills).

**Output rules:** declare your pin; quote exact text for every ruling; if a URL fails for you, say so and mark the item unverifiable rather than substituting remembered text.
