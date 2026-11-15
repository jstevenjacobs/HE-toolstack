# Ticket D-14 — Canonical backup root (user ruling, 2026-11-15)

**Goal:** design must specify `/mnt/c/Users/steven/OneDrive/Backup/HE-toolstack` as the root
directory for ALL backups.

**Done-check:**
- [x] Path verified on host + container-visible WSL path + free space (841 GB) + `HE-toolstack/` exists.
- [x] NFR-22 added (REQ v1.1) + matrix row; ADR-D-14 Accepted (v1.1); X-8 scope note (hot-path ban vs cold backup carve-out).
- [x] TD: new §6.9 backup component; §9.1/§9.4/§12.2/D8/R-4 rewritten to backup-root; new runbook R-8; env `BACKUP_ROOT`; §3 counts 63->64 IDs.
- [x] REVIEW O6 + QA Q13 (rev v1.1); residual-destination sweep clean (only demoted/alternative mentions remain).
- [x] Mermaid re-validation post-D8 edit: 8/8 parse OK.

**Result:** ruling propagated across all five Phase 2 docs + workflow files.
