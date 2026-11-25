# M0 Interview Transcript

Rows are sha256-chained: each row's `prev` field is the sha256 of the previous row
line (row 0's prev = the protocol file's sha256). Owner answers verbatim, unedited.

| # | prev | date | question (id) | owner answer (verbatim) | evidence |
|---|------|------|---------------|--------------------------|----------|
| 0 | — | 2026-11-25 | (seed) protocol file `workflows/m0-interview-protocol.md` committed at this branch | — (no answer required; seed row) | prev=99fcc7741d8ccb7afb1f9aab7d28f3051b83438e4f42402228e7662cbbd66a6a |

- **Chain note 3** (rev-3): protocol rev-3 (round-2 amendments: §3 broker architecture; Grok ACCEPT + ChatGPT ACCEPT-WITH-CHANGES at `2951d35`). New sha256(sha256-prev||row). Prev = chain note 2.
