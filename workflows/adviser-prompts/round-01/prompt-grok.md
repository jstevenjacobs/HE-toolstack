# Council prompt R1b-grok — HE-toolstack final design review (round 1 of deployment planning)

**STATE.** Repo: https://github.com/jstevenjacobs/HE-toolstack — GitHub is the single source of truth for this council. Design package on `main` at `5c487f4` (DESIGN-v2, DEPLOY-v2, TD v1.13, REQ v1.10, ADR v1.11 incl. D-15 Option D + D-16 Option B ACCEPTED, QA v2.3 claiming 27/27 gates, REVIEW-RESPONSE through r13). PR #12 (open) adds the deployment-planning inputs: residual-risk register R-01..R-12 (`workflows/residual-risks-DP0.md`), 11 candidate tickets (`workflows/tickets/candidates/`), an action plan (`workflows/DEPLOYMENT-PLANNING-PLAN.md`), and a self-contained package (`workflows/for-adviser-review-2026-11-22.md`). Read them at the permalink: https://github.com/jstevenjacobs/HE-toolstack/tree/dp/round-01-dp0 (or after merge, at main <POST-MERGE-SHA>).

**ROLE — **Live-verification adviser.** Every technical claim you rely on must carry a retrieved source (URL + access date) — not your model's memory. Prefer primary sources (Docker/docs/github issues/specs).**

**QUESTIONS (answer each, numbered):**
1. D-16 Option B: a sidecar exposing exactly four ops (create_run / inspect-or-status / kill / logs) with the engine never seeing the Docker socket. Verify against current Docker Engine API / SDK docs: any capability the four-op surface cannot express that TD §6.2b needs at M0 (CPU-only, one compose project)? Cite.
2. TD §8.8 claim protocol is flock-based (r3) on ext4. Verify fcntl/flock semantics under the failure classes the T-matrix exercises (T-20 mutual exclusion, T-21 stale-claim supersede, crash during hold): does flock release on process crash and on container kill (SIGKILL) per upstream docs? Any known kernel/containerd caveat? Cite.
3. C3 (orphan `infra-minio-1` teardown): MinIO is currently a lone container in an `infra` compose project next to a healthy Cognee stack. For a teardown + volume purge, what is the correct upstream-documented removal sequence, and what data-loss trap should the done-check guard? Cite.
4. R-10 claims the QA report's Q22 row is truncated on disk at 248 bytes so '27/27' is not text-verifiable in the repo. Open docs/HE-TOOLSTACK-QA-REPORT.md at the permalink, find the Q22 row, and report exactly what is missing. URL + permalink used.
5. D-15 Option D: single compose project with zero host publication for toolserver. Verify current compose docs: ports exposed only via `expose`/network + healthcheck without `ports:` — any gotcha (e.g. healthcheck hitting a non-published port from inside the network) that would break TD §7.2's /healthz /readyz /deps trio? Cite.

**REPLY FORMAT (paste back verbatim; it will be committed under `workflows/adviser-input/` unchanged):**
VERDICT: APPROVE | APPROVE-WITH-CHANGES | VETO
FINDINGS: numbered; each = [blocker|major|minor|nit] + one-paragraph argument
ANSWERS: numbered to match the questions above
Quorum rule: 2 of 3 adviser replies required to proceed; a missing reply is recorded as `no-reply`, never treated as consent.
