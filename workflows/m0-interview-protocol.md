# M0 Interview Protocol (Round-07)

**Purpose.** Progress through the M0 gate with the human operator contributing only
judgment, never manual labor. Every mechanical act — typing commands, running drills,
assembling evidence, drafting text — is performed by Hermes. Every mechanical claim is
verified by the council against pinned evidence. The owner's contributions are short
spoken/written answers to numbered questions, recorded verbatim.

**Precedent.** This is the round-05 interview pattern (engineering walk: one line per
row, transcript pinned, council cross-examined) extended from paper rows to live M0
execution. The council accepted the pattern's discipline at `adca8a4`; nothing here
weakens it — it only removes keystrokes from the human path.

## Roles

- **Hermes (executor + scribe):** runs every command, writes every artifact, commits
  all evidence. Poses one question at a time.
- **Owner (interviewee):** answers numbered questions, one sentence each. The verbatim
  recorded answer IS the signature (this is what §9's authority-signature rows require
  from the single human: a recordable act of authority, not typing labor).
- **Council (Grok + ChatGPT, quorum 2/2):** validates every evidence row from pinned
  SHAs + verbatim transcripts, exactly as in rounds 05/06. Verdicts close rows.

## Hard rules

1. **One question at a time.** Format: context ≤3 lines → the single decision →
   (optionally) Hermes's recommendation. No batches, no forms.
2. **Owner answers give authority and preference only — never technical claims.**
   Pass/fail of any T-test comes from command output evidence committed to git, not
   from anyone's recollection (the round-05 unmeasured-vocalization rule, inverted:
   the human stops being a measurement source entirely).
3. **Exactly three things require an owner answer** — nothing else may:
   - (a) **approval** of destructive/irreversible operations on real data (each one,
     individually — blanket approvals not accepted);
   - (b) **risk acceptance** (e.g. F-1 sidecar authN/Z posture);
   - (c) **authority signatures** (§2b checklist confirmations, QA §5 disclosure,
     §9 rows, M0 CLOSED) — each = one verbatim sentence.
   Rulings on open decisions (D-06/07/11/17/18, OQ-9) are (c)-class: Hermes presents
   options + recommendation; owner answers with the ruling sentence.
4. **Cold-session integrity (T0.5):** the cold-session answer must be produced in a
   fresh session with zero carried context — structurally impossible for Hermes to
   fake. Owner contribution: open a new session and paste ONE line that Hermes
   prepares. This is the only place the owner touches a keyboard beyond talking.
5. **Destructive-op pacing:** each wave's approvals are collected in the interview,
   but execution is gated: nothing irreversible runs until the council ACCEPTs this
   protocol (PR #17) and the specific op's blast radius has been presented in the
   question itself.
6. **Every wave closes with:** evidence committed → council prompt issued → verdicts
   recorded in the ledger → next wave. Status discipline unchanged: executed ≠ passed
   ≠ authorized; drafts ≠ passes.

## Waves

| Wave | Content | Owner input (est.) |
|---|---|---|
| 0 | Protocol ACCEPT + M0 authorization + rulings D-06/07/11/17/18, F-1 posture, OQ-9 | ~8 one-sentence answers |
| 1 | Pass-C: C1/C2 build-only (no question); C3/C4/C5 approvals ×3, Hermes executes teardowns/archives | 3 one-word-class approvals |
| 2 | T0.1→T0.4 build chain executed by Hermes; zero questions unless a ruling is forced; T0.5 cold-session paste | 1 paste |
| 3 | T0.6 `make verify` chain + drills (T-13 full, T-15 six-leg, T-16, T-19, host-reboot) + R-4/R-5/R-7 live runbook walks w/ T-11-class evidence | 0 |
| 4 | Signatures: §2b confirmations, QA §5, M0 CLOSED; council 2/2 on full evidence pack | ~10 one-sentence answers |

**Total expected owner labor: ~20 sentences + 1 paste. No typing of commands, no
assembly, no transcription work.**

## Transcript

`workflows/m0-interview-transcript.md` — one entry per question: id, timestamp, the
question as asked, the owner's verbatim answer, the evidence link. sha256-chained rows.
Council receives pinned raw-URLs to this file plus per-wave evidence dirs.
