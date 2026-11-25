# Walk predicates — pinned tree 5a24b0c (committed BEFORE the interview; no candidate answers in this file)

Walk: owner engineering rows M1, M2, M4, M6, M8, M9 per DESIGN-REVIEW §2b, executed via
INTERACTIVE PROTOCOL v2 (engineering-walk-interactive.md). Pinned tree: branch
dp/round-05-signoff-scheme @ `5a24b0c` (D1–D9 + §2b byte-identical to main @ 79beb57;
branch delta touches only TD §16, ADR OQ-9 row, register, ledger — no diagrams). Diagram→
block map (TD Appendix B + measured block lines): D1 §5.1 L225–251 · D2 §5.2 L262–293 ·
D3 §5.3 L312–331 · D4 §5.3 L339–347 · D5 §8.1 L1030–1039 · D6 §8.3 L1063–1071 ·
D7 L1759–1783 · D8 L1786–1804 · D9 §6.10 L895–911.

Disclosed caveat: the interviewing agent is the package author; mitigations per protocol v2
(quote-or-invalid, counter-example search, DEFECT-by-default, 2-of-6 human spot-checks,
ChatGPT blind falsification, committable transcript).

## M1 — spawn routing (question verbatim from §2b)
Q: Does every spawn edge (D1/D3/D4) route **only** through the spawn-sidecar's 4 HTTP ops
(TD §6.2b), with no engine/sidecar socket mount and no fifth `reap` edge?
FAIL if: any edge spawns/solves/kills a job without passing through the sidecar's 4-op set;
engine node carries a docker-socket mount label; any engine-facing 5th op or `reap` edge in
D1/D3/D4. Mandatory counter-example greps over block text D1,D3,D4: `reap`, `sock` (edges
whose tail is the engine/workflow-engine node and head is a job/docker-daemon node), any
spawn verb not paired with `HTTP`. Prose anchor: TD §6.2b ops list + "not an engine-facing
method" janitor sentence.

## M2 — sole-holder + root-equivalent label
Q: Do D2/D3/D4 name the sidecar as **sole docker.sock holder** *and* carry the
root-equivalent-if-compromised label (D-16 ACCEPTED caveat)?
FAIL if: any of D2/D3/D4 lacks a sidecar node entirely, or the sidecar node lacks the
"sole … holder" phrase, or lacks "root-equivalent" caveat text. Greps per block: `sidecar`,
`sole`, `root-equivalent`. (A missing node counts as a missing label — DEFECT by default;
operator may downgrade with reason.)

## M4 — D3 network inventory exactly 4 entries, no alt-arch subgraph
Q: Does D3's network inventory enumerate exactly `he-edge / he-agent / he-internal /
/var/run/he-runs` with no legacy alt-architecture subgraph?
FAIL if: any he-* / bind-mount path label in D3 outside the set of four; any subgraph
representing Option A/C remnants (tokens: `Option A`, `Option C`, `systemd`, `engine.sock`,
alternative engine-as-socket-holder nodes). Greps: all `he-` tokens + all subgraph titles in D3.

## M6 — ticket/run state edges vs §8.1/§8.8 claim semantics
Q: Do D5/D6 ticket-state edges match §8.1/§8.8 claim semantics (flock at execution time;
supersede after kernel-released lock)?
FAIL if: D5 lacks the flock-at-claim/execution-time edge label; supersede-after-lock-release
semantics have NO counterpart in D5/D6 prose-adjacent diagram text; any D6 edge implying
promotion without gate-pass (contradicts §8). Greps: `flock`, `supersede`, `kernel` in D5/D6
blocks + §8.8 sentence the diagram must mirror.

## M8 — diagram node names == §6 component names (both directions)
Q: Do diagram node names equal §6 component names (no drift in either direction)?
FAIL if: any displayed node LABEL in D1–D9 names a §6 component with a different name
(e.g. "engine" vs "workflow-engine", bare "sidecar" vs "spawn-sidecar"), or a §6 component
with required diagram presence appears nowhere. Greps: extracted label set D1–D9 vs §6
component-name list (workflow-engine, spawn-sidecar, toolserver, heat-data, minio, git
ledger/remote, runner, queue, candidate registry, gpu-admission).

## M9 — canonical health trio only
Q: Does every health/readiness label agree with the canonical trio `/healthz` `/readyz`
`/deps` (no `/health`)?
FAIL if: any `/health` (exact token, not `/healthz`) in D1–D9 block text or in the prose
rows naming health endpoints for these components. Greps: `"/health"` with word-boundary
(negative for healthz/healthcheck context), plus every health label found in blocks for
agreement check.

## Pass standard
Row PASS = operator YES to a shown pair (prose quote + diagram label) with counter-example
report clean; missing evidence = DEFECT default (operator may downgrade, one-line reason);
operator may request "show more" freely. Spot-check phase: operator picks 2 of 6 rows,
verifies quoted text in pinned tree themselves; mismatch reopens that row.
