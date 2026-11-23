Merge PR#13 after the minor remediation requested

GROK:
---------------------------------
Sanity-check: PASS (with one minor precision note)

The reworded clause at 5de9781 is accurate and strictly better than the prior version.

Current wording (loaded from live GitHub)
flock is bound to the open file description, not the pathname, and is released by the kernel when the last fd referencing that file description closes — process death closes that process’s fds, so any exit or signal including SIGKILL and container kill releases the lock as the kernel reaps each process. Caveat stated explicitly [DP-R2a 2026-11-23 clarification]: an fd inherited via fork/exec or duplicated to another process keeps the lock alive after the original holder dies — hence the claim process stays single-process (§8.8 claim model) and must not leak the lock fd across fork+exec; T-20’s crash leg includes this inheritance check. No unlink protocol, no stale-lock sweep, no delete/recreate race — a leftover lock file with no live fd is simply unlocked.

Cross-check against kernel semantics
Claim in the clause	Kernel fact (flock(2) / open-file-description model)	Status
Bound to the open file description, not the pathname	Correct. flock locks attach to the open-file description (struct file), not the inode path or dentry.	Exact
Released when the last fd referencing that description closes	Correct. Duplicate fds (dup / fork inheritance) share the same lock; the lock persists until the last one is closed.	Exact
Process death (any exit / SIGKILL / container kill) closes that process’s fds	Correct. The kernel closes every open fd during do_exit / task reaping, including after SIGKILL.	Exact
Inheritance via fork/exec or explicit duplication keeps the lock alive after the original holder dies	Correct and necessary caveat. This is the classic “leaked lock fd” case.	Exact
Design implication: claim process stays single-process and must not leak the fd	Correct operational consequence of the above.	Sound
Leftover lock file is inert	Correct — the file is just a name; the lock state lives only while an open-file description holds it.	Exact
Source: [man7.org/linux/man-pages/man2/flock.2.html](https://man7.org/linux/man-pages/man2/flock.2.html) (accessed 2026-11-23) — “Locks created by flock() are associated with an open file description … the lock is released … when all such file descriptors have been closed.”

Minor precision note (non-blocking)
The phrase “as the kernel reaps each process” is slightly loose. Reaping (wait/waitpid) is performed by the parent; the fd close and lock release happen earlier, during the dying process’s own exit path, before it becomes a zombie. In practice this never matters for the claim protocol (the lock is gone by the time any other process can observe the PID as dead), so the wording remains operationally correct. A pedantic alternative would be “as the kernel tears down the process,” but the current text is fine.

Conclusion
The rewording is faithful, complete, and correctly incorporates the inheritance edge-case that was previously only an advisory note. No further change is required for technical accuracy.

CHATGPT:
-------------------------------------------------------
R2a follow-up review — commit 4bcdbc4
Disposition: APPROVE-WITH-CHANGES — items 1 and 2 are closed; item 3 is only partially closed; item 4 is recorded as closed but not independently verifiable.

I reviewed commit 4bcdbc437eed4d110f05b49210b35bb54c797f33 and the affected files at that exact SHA.
#	Previous finding	Status	Assessment
1	Q22 reconstruction	Closed	The repaired QA row retains the r3 wording, completes the sentence, and includes the repair annotation. The evidence explains why the r2 wording was not copied wholesale.
2	Errata annotations and typo	Closed	TD §8.8 now includes the DP-R2a annotation. The evidence typo is corrected to r13-era. No version bump is warranted.
3	flock open-file-description semantics	Partially closed	The technical explanation now correctly identifies the open file description and the inherited-descriptor caveat. However, the referenced T-20 inheritance test is not actually specified in the normative T-20 requirement.
4	Q22 predicate must include T-20	Recorded; not independently verified	The evidence and final gate log report the predicate extension and 27 PASS / 0 FAIL. The harness itself is still absent from the repository, so I cannot inspect or execute the changed predicate.

Details requiring attention
1. Q22 reconstruction — closed
The repaired row in docs/HE-TOOLSTACK-QA-REPORT.md is coherent with the current T-20 through T-23 definitions. The accompanying evidence explains the reconstruction method and preserves the distinction between reusing the predecessor's sentence construction and reusing obsolete technical wording.

I have no additional objection to this repair.
2. Documentation corrections — closed
The missing TD annotation is now present in §8.8, and the evidence file uses r13-era. Retaining the existing document versions remains reasonable for these documentation-only corrections.
3. flock semantics — one remaining change
The revised TD §8.8 wording is substantially correct. In particular, it now explains that the lock survives the original holder's death if another process retains a reference to the same open file description.

However, there is a mismatch:
- TD §8.8, lines 1155–1159, says T-20's crash leg includes an inheritance check.
- REQ T-20, in docs/HE-TOOLSTACK-REQUIREMENTS.md, specifies killing the holder with kill -9 and verifying that a fresh claimant can acquire the lock. It does not specify testing a fork-inherited or duplicated descriptor.
That matters because a test that merely kills the original holder does not demonstrate that the implementation handles descriptor inheritance correctly.

Required correction: Add an explicit descriptor-inheritance case to T-20. It should verify that a forked child retaining the lock descriptor keeps the lock held after the original claimant dies, and that the lock becomes available only after the final reference closes. Also verify that the production claim process does not leak the descriptor across fork/exec.

This is a small requirements/test-specification correction, not an architecture change.
4. Q22 predicate — evidence accepted, implementation not independently verified
The new gate-run-r2a-final.txt reports:
- Q22 PASS — T-20 through T-23 defined and matrixed.
- Total: 27 PASS / 0 FAIL.
The evidence says the predicate now explicitly checks T-20 in both the matrix and requirements table. That is the right correction.

But gates_v13.py remains outside the repository. The processing log explicitly acknowledges this. Consequently, I can confirm that the repository records the correction and its reported result, but I cannot independently establish that the executable predicate contains the claimed checks.

I would not block this documentation repair solely on the missing harness, since that is already tracked for R2c. It must, however, remain an explicit verification limitation—not be represented as independently reproduced.

Final recommendation
Do not require another broad review or a version bump. Make the small T-20 requirement correction so its actual acceptance criteria match the inheritance check now promised by TD §8.8.

After that correction, I would consider all four of my R2a findings closed for purposes of PR #13, with the harness-verification limitation carried forward to R2c.

The PR remains open in GitHub; this is my review disposition, not a merge action.