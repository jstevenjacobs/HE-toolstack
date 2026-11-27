#!/usr/bin/env python3
"""m0-broker-runner.py — M0 interview protocol §3.3/§3.4 plan-gated broker (rev-7).

Runs as the m0broker account (systemd). Fails CLOSED everywhere: an unverifiable plan
authorizes nothing; unchecked git failures stop the loop rather than continue on stale
state; nothing is ever "processed" until its evidence is durably stored AND pushed.

rev-7 repairs (ChatGPT re-pin-5 REJECT at 3f3b04a + Claude re-pin-5 required change):
- ID-COLLISION BEFORE LIFECYCLE: the request-id/hash comparison now runs before
  every lifecycle branch INCLUDING 'started' — a conflicting line can no longer
  masquerade as the original's UNPROVEN outcome; both hashes always preserved
  (ChatGPT blocker 1).
- KNOWN OUTCOMES NEVER DEGRADE: on restart, a 'started' request first consults its
  durable record — spawn_succeeded=False recovers as definite spawn failure, a
  completion record recovers as executed; UNPROVEN only when genuinely uncertain
  (ChatGPT blocker 2).
- BUDGET FAILS CLOSED: corrupt/unparseable durable usage state refuses with
  BUDGET-STATE-CORRUPT instead of silently reading as zero uses (ChatGPT blocker 3).
- UNVERIFIABLE PLAN IS NEVER TERMINAL: absent, unsigned, signature-failed, or
  structurally broken plan => all requests stay PENDING (Claude re-pin-5 required
  change — closes the out-of-order plan/sig commit window and the push-attacker
  blacklist vector).
- Per-command use budget key (argv+artifacts+max_runs, not whole-plan digest), so a
  re-sign that only adds commands cannot reset consumed budgets (Claude).
- Spawn exception scope broadened OSError -> Exception (NUL byte / empty argv can no
  longer crash the pass after 'started'); malformed argv rejected at plan
  verification (Claude).
- Directory-entry durability: durable_write fsyncs the full untracked ancestor
  chain to the filesystem root (ChatGPT P1).

rev-6 repairs (ChatGPT re-pin-4 REJECT at 8509096 + Claude re-pin-4 conditions):
- REAL fsync durability: durable_write() fsyncs the temp file AND the parent
  directory after rename, so state/record/refusal transitions survive a host
  crash/power loss, not just a process restart (ChatGPT repair 1).
- Request-ID collision detection: a reused id whose line hash differs from the
  stored disposition gets an explicit ID-COLLISION refusal preserving BOTH
  hashes; identical-hash replays stay silent-as-duplicate by design
  (ChatGPT repair 3).
- Pinned artifacts verified BEFORE spawn: plan entries pin {path, sha256} for
  every script they execute; the signature digest now covers argv + artifact
  hashes + max_runs, and a mismatch/missing refuses without executing
  (Claude condition 1 + open question: branch-pushers can no longer swap the
  scripts under a valid signature).
- Signed use budget: max_runs per command, counted durably by
  plan_digest+argv_digest — a fresh request id cannot re-burn a used command
  (Claude condition 2).
- Unverifiable-plan rule (§3.3): plan FILE ABSENT -> requests stay PENDING (a
  later signature can authorize them); plan PRESENT but invalid signature ->
  refuse on record (Claude condition 3).
- Spawn failures (OSError, e.g. missing binary) are DEFINITE failure records,
  never left as uncertain 'started' (Claude condition 4).

rev-5 repairs (ChatGPT re-pin-3 REJECT at 1ce2b3c — the five P0s):
- DURABLE REQUEST STATE: every request carries a lifecycle file under
  <state_dir>/state (started BEFORE exec, executed after, published after a
  confirmed push). The in-memory processed-set is gone; a systemd restart cannot
  replay an executed operation.
- UNPROVEN semantics: a request whose state reads "started" at recovery time is
  first reconciled against its durable record (rev-7) — definite outcomes never
  degrade to UNPROVEN. A GENUINELY uncertain 'started' (no usable record) gets an
  UNPROVEN refusal and NEVER auto-reruns; a second attempt requires a separate,
  explicit owner recovery decision.
- Evidence durability: record/refusal files are authored in broker-owned
  <state_dir> FIRST and copied into the evidence worktree at publish time, so
  `git reset --hard` or a failed push can never destroy unpublished evidence.
- No silent drops: every queue line gets a broker-committed disposition —
  valid+authorized executes; valid+unauthorized refuses; malformed JSON and
  missing/invalid request IDs produce invalid-request refusal records.
- Real --once mode (default: exactly one fetch/process/publish cycle, then exit;
  exit 3 if publication is pending). --daemon loops. Rev-4's prompt claimed
  --once existed; it did not — correction on record, ChatGPT re-pin-3 §3.
- Owner principal is read from broker config, matching §3.3 (rev-4 doc said the
  plan declared it; the protocol text is corrected to match this code).

Not installed or run until protocol ACCEPT and owner-run provisioning (m0-broker-setup.sh).
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, subprocess, sys, time
from pathlib import Path

PLAN_PATH = "workflows/m0-plans/open.json"
PLAN_SIG_PATH = "workflows/m0-plans/open.json.sig"  # ssh-keygen -Y sign writes <file>.sig
QUEUE_PATH = "workflows/m0-evidence/requests.jsonl"
RECORD_DIR = "workflows/m0-evidence/records"
REFUSAL_DIR = "workflows/m0-evidence/refusals"
PUSH_FAIL_LIMIT = 5
STATE_DEFAULT = "/opt/m0-broker/state"

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def log(msg: str) -> None:
    print(f"[m0-broker {now()}] {msg}", flush=True)

def git_checked(repo: str, *args: str) -> str:
    r = subprocess.run(("git", "-C", repo, *args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed rc={r.returncode}: {r.stderr.strip()[:400]}")
    return r.stdout.strip()

def canonical_sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _sync_dir_chain(directory: Path) -> None:
    """rev-7 (ChatGPT re-pin-5 P1): syncing a directory persists its CONTENTS, not
    the directory's own ENTRY in its parent. When durable_write first creates a
    nested layout (state/, records/, refusals/ under a fresh M0 root), each new
    directory's entry must be synced through its parent chain up to the mount."""
    chain = []
    cur = directory
    while len(chain) < 16:
        chain.append(cur)
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    for d in reversed(chain):  # deepest first, ancestors last
        try:
            fd = os.open(str(d), os.O_DIRECTORY)
        except OSError:
            return  # vanished mid-sync; nothing safe left to sync
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

def durable_write(path: Path, obj) -> None:
    """Crash-consistent write (rev-6 ChatGPT re-pin-4 repair 1; rev-7 hardening):
    write a temp file, fsync it, atomically replace the destination, then fsync
    the parent directory AND its untracked ancestors so both the rename and the
    entries of newly-created nested directories survive abrupt power loss.
    Atomic replacement alone only survives process restart."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, indent=2))
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    _sync_dir_chain(path.parent)

class Ledger:
    """Durable per-request state + evidence, OUTSIDE the git worktree (a
    `reset --hard` between passes must never destroy execution history)."""
    def __init__(self, root: str):
        self.root = Path(root)
    def state(self, rid: str) -> Path:
        return self.root / "state" / f"{rid}.json"
    def record(self, rid: str) -> Path:
        return self.root / "records" / f"{rid}.json"
    def refusal(self, rid: str) -> Path:
        return self.root / "refusals" / f"{rid}.json"
    def load(self, rid: str) -> dict | None:
        p = self.state(rid)
        return json.loads(p.read_text()) if p.exists() else None
    def save(self, rid: str, status: str, note: str = "", req_hash: str = "") -> None:
        durable_write(self.state(rid), {
            "id": rid, "status": status, "updated": now(), "note": note,
            "request_line_sha256": req_hash})
    def pending(self) -> list[str]:
        """LEDGER KEYS with a local disposition not yet confirmed pushed. The key
        is the state-file stem (rev-6: collision dispositions live under their own
        key so they can never overwrite the original request's files)."""
        out = []
        d = self.root / "state"
        if d.is_dir():
            for f in d.glob("*.json"):
                try:
                    st = json.loads(f.read_text())
                except json.JSONDecodeError:
                    continue
                if st.get("status") in ("executed", "dispositioned"):
                    out.append(f.stem)
        return out

def verify_plan(repo: str, allowed_signers: Path, principal: str) -> dict:
    """Return {status, commands:{digest: {argv, artifacts, max_runs}}, wave,
    plan_digest, signed_by}. The rev-7 §3.3 rule (Claude re-pin-5 required change
    extends the rev-6 absent-plan rule):
      'unverifiable' — plan absent, unsigned, signature-failed, or structurally
                  broken: requests stay PENDING (no disposition; a later valid
                  owner signature supersedes; unverifiable is NEVER terminal, so
                  a push-capable attacker or an out-of-order plan/sig pair can no
                  longer permanently blacklist ids);
      'valid'   — owner-signed and internally consistent: authorizes.
    Only a VALID plan may ever lead to execution; a VALID plan that does not
    contain the request's digest is a genuine verified denial -> refuse."""
    plan_file, sig_file = Path(repo) / PLAN_PATH, Path(repo) / PLAN_SIG_PATH
    status = {"status": "unverifiable", "commands": {}, "wave": None,
              "plan_digest": None, "signed_by": None}
    if not plan_file.exists():
        # True absence (not yet published) => unverifiable, NOT verified-absent.
        status["why"] = "plan file absent — requests remain pending"
        return status
    if not (sig_file.exists() and allowed_signers.exists()):
        # rev-7 (Claude re-pin-5 REQUIRED change): plan present but unsigned is
        # authorization UNVERIFIABLE, not a permanent denial — requests stay
        # PENDING. Terminal refusals here let anyone with branch push rights plant
        # an unsigned plan to blacklist arbitrary ids, and a plan-commit landing
        # before its signature-commit would blacklist the ids in between. A later
        # valid signature supersedes. (Security EVENT still gets logged loudly.)
        log("PLAN-EVENT: plan present but signature/signer file missing — "
            "requests remain pending (rev-7: unverifiable is never terminal)")
        status["why"] = ("plan present but signature/signer file missing — "
                         "requests remain pending until a valid owner signature "
                         "supersedes")
        return status
    v = subprocess.run(
        ("ssh-keygen", "-Y", "verify", "-f", str(allowed_signers), "-I", principal,
         "-n", "file", "-s", str(sig_file)),
        stdin=open(plan_file, "rb"), capture_output=True, text=True)
    if v.returncode != 0:
        # Same rule for a signature that FAILS: pending, never terminal (§3.3 rev-7;
        # an attacker-pushed bad plan can no longer permanently refuse queued ids).
        log(f"PLAN-EVENT: plan signature FAILED owner verification — {v.stderr.strip()[:200]}")
        status["why"] = ("plan signature FAILED owner verification — requests remain "
                         "pending; a later valid owner signature supersedes")
        return status
    try:
        plan = json.loads(plan_file.read_text())
    except json.JSONDecodeError as e:
        # rev-7: structurally unreadable body => unverifiable (pending), same rule.
        status["why"] = f"plan JSON invalid ({e}) — requests remain pending"
        return status
    commands = {}
    payloads = []
    for c in plan.get("commands", []):
        argv = c.get("argv")
        artifacts = c.get("artifacts", [])
        if not isinstance(artifacts, list) or any(
                not isinstance(a, dict) or not isinstance(a.get("path"), str)
                or not isinstance(a.get("sha256"), str) for a in artifacts):
            status["why"] = "plan artifacts malformed (need {path, sha256}) — requests remain pending"
            return status
        max_runs = c.get("max_runs", 1)  # rev-6 use budget (Claude re-pin-4 cond. 2)
        if not isinstance(max_runs, int) or isinstance(max_runs, bool) or max_runs < 1:
            status["why"] = "plan max_runs must be a positive integer — requests remain pending"
            return status
        if isinstance(argv, list) and argv and all(
                isinstance(x, str) and "\x00" not in x for x in argv):
            commands[canonical_sha256(argv)] = {"argv": argv, "artifacts": artifacts,
                                                "max_runs": max_runs}
            # plan_digest covers argv AND pinned artifact hashes AND the budget:
            # the owner signature therefore protects the scripts themselves, not
            # just the command line (Claude re-pin-4 condition 1 + open question).
            payloads.append(canonical_sha256({"argv": argv, "artifacts": artifacts,
                                              "max_runs": max_runs}))
        else:
            # rev-7 (Claude re-pin-5): an EMPTY argv or a NUL byte inside argv is a
            # PLAN error, not a runtime spawn crash — rejected here so the broker can
            # never write 'started' and then die on ValueError/IndexError, which
            # would strand the request as UNPROVEN on restart.
            status["why"] = ("plan entry argv malformed (empty, non-string, or NUL "
                             "byte) — requests remain pending")
            return status
    if canonical_sha256(sorted(payloads)) != plan.get("plan_digest", ""):
        status["why"] = ("plan_digest does not match command set "
                         "(argv/artifacts/max_runs) — requests remain pending")
        return status
    return {"status": "valid", "commands": commands, "wave": plan.get("wave"),
            "plan_digest": plan.get("plan_digest"), "signed_by": principal}

def digest_artifacts(base: Path, artifacts: list) -> dict:
    """Pre-spawn verification (rev-6, Claude re-pin-4 condition 1): every artifact
    a plan command depends on is hashed and compared to the owner-signed hash.
    Returns {path: observed_sha256}; any mismatch/missing means refuse, don't run.
    Whoever can push to the evidence branch can otherwise swap the very scripts
    the broker executes — the signature only protects them if their hashes are
    pinned in the signed plan and verified before spawn."""
    out = {}
    for a in artifacts:
        p = base / a["path"]
        observed = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
        out[a["path"]] = {"observed": observed, "pinned": a["sha256"],
                          "match": observed == a["sha256"]}
    return out

def usage_count(L: Ledger, use_key: str):
    """Executions recorded for one signed command authorization. rev-7 keying
    (Claude re-pin-5): USE key = canonical_sha256(argv + artifacts + max_runs) —
    NOT the whole-plan digest. A deliberate re-sign that only ADDS a new command
    must not reset the use budget of commands that already consumed theirs.
    rev-7 fail-closed (ChatGPT re-pin-5 blocker 3): returns int on OK, or a
    'CORRUPT:<detail>' string when the durable usage file exists but cannot be
    parsed/holds a non-int count — the CALLER must refuse, never treat corrupt
    budget state as zero uses."""
    p = L.root / "usage" / f"{use_key}.json"
    if not p.exists():
        return 0  # genuinely never initialized
    try:
        body = json.loads(p.read_text())
        n = body.get("count")
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise ValueError(f"count not a non-negative int: {n!r}")
        return n
    except (json.JSONDecodeError, ValueError) as e:
        return f"CORRUPT:{e}"

def bump_usage(L: Ledger, use_key: str) -> int:
    p = L.root / "usage" / f"{use_key}.json"
    cur = usage_count(L, use_key)
    if isinstance(cur, str):  # corrupt budget file: caller should have refused
        raise RuntimeError(f"BUDGET-STATE-CORRUPT at bump: {cur}")
    n = cur + 1
    durable_write(p, {"use_key": use_key, "count": n, "updated": now()})
    return n

def record_history_count(L: Ledger, argv, artifacts, max_runs) -> int:
    """Executions of THIS command visible in durable completion records (rev-7).
    Two purposes: (a) the use-budget counter file lives in broker state and would
    reset if state is wiped — records are the audit history, so the budget reads
    max(counter, history) (Claude re-pin-5: budgets must not reset on re-sign /
    state loss); (b) records with spawn_succeeded=False (never spawned) do NOT
    count against the budget — a failed spawn consumed no execution."""
    d = L.root / "records"
    if not d.exists():
        return 0
    n = 0
    for f in sorted(d.glob("*.json")):
        try:
            rec = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict) or rec.get("spawn_succeeded") is False:
            continue
        if (rec.get("argv") == argv and rec.get("max_runs") == max_runs
                and rec.get("artifact_contract") == artifacts):
            n += 1
    return n

def load_config() -> dict:
    """Broker config written at provisioning; systemd needs no CLI flags."""
    cfg = Path.home() / ".m0-broker.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def refuse(L: Ledger, rid: str, reason: str, req_hash: str = "",
           extra: dict | None = None, key: str | None = None) -> None:
    """Durably author a refusal record + mark the request dispositioned. Refusals
    have no side effects, so this is safe to record before any push. `key` (rev-6)
    lets a secondary refusal (e.g. an ID-collision against an already-disposed id)
    live under its own ledger key WITHOUT overwriting the original disposition."""
    body = {"id": rid, "refused_at": now(), "request_line_sha256": req_hash,
            "reason": reason}
    if extra:
        body.update(extra)
    k = key or rid
    if key:
        body["ledger_key"] = key
    durable_write(L.refusal(k), body)
    L.save(k, "dispositioned", note=reason, req_hash=req_hash)
    log(f"REFUSED {k}: {reason}")

def run_pass(a, allowed_signers: Path, L: Ledger) -> int:
    """One fetch/process/publish cycle. Returns 0 ok, 2 fetch/reset failure,
    3 publication still pending (caller retries or exits)."""
    try:
        git_checked(a.repo, "fetch", "origin", a.branch)
        git_checked(a.repo, "reset", "--hard", f"origin/{a.branch}")
    except RuntimeError as e:
        log(f"PASS FAIL (fetch/reset): {e}")
        return 2
    plan = verify_plan(a.repo, allowed_signers, a.owner_principal)
    q = Path(a.repo) / QUEUE_PATH
    # rev-7 (Claude re-pin-5): read the queue as BYTES and decode per line, so one
    # undecodable byte cannot raise UnicodeDecodeError and kill the whole pass.
    # An undecodable line gets the same invalid-request disposition as malformed
    # JSON, hashed over its raw bytes.
    raw_lines: list[bytes] = []
    if q.exists():
        raw_lines = [ln for ln in q.read_bytes().split(b"\n") if ln.strip()]

    for raw_b in raw_lines:
        try:
            raw = raw_b.decode("utf-8")
        except UnicodeDecodeError as e:
            req_hash = hashlib.sha256(raw_b).hexdigest()
            rid = f"invalid-{req_hash[:16]}"
            if not L.load(rid):
                refuse(L, rid, f"invalid-request: queue line not valid UTF-8 ({e}) "
                               f"— §3.4 fail closed", req_hash)
            continue
        if not raw.strip():
            continue
        req_hash = hashlib.sha256(raw.encode()).hexdigest()
        # --- every line gets a disposition: nothing disappears silently (rev-5 P0) ---
        try:
            req = json.loads(raw)
            if not isinstance(req, dict):
                raise json.JSONDecodeError("not an object", raw, 0)
        except json.JSONDecodeError as e:
            rid = f"invalid-{req_hash[:16]}"
            if not L.load(rid):
                refuse(L, rid, f"invalid-request: malformed queue line ({e})", req_hash)
            continue
        rid = req.get("id")
        if not isinstance(rid, str) or not rid or not rid.replace("-", "").replace("_", "").isalnum():
            rid = f"noid-{req_hash[:16]}"
            if not L.load(rid):
                refuse(L, rid, "invalid-request: missing or invalid request id", req_hash)
            continue
        st = L.load(rid)
        # --- rev-7 blocker 1 (ChatGPT re-pin-5): ID-COLLISION is checked BEFORE
        # every lifecycle-state branch, including 'started'. A request id must
        # always identify one exact request content; the collision evidence must
        # preserve BOTH hashes and must not be preempted by started-recovery, or a
        # conflicting line would masquerade as the original's UNPROVEN outcome.
        if st:
            prior_hash = st.get("request_line_sha256", "")
            if prior_hash and prior_hash != req_hash:
                collision_key = f"{rid}-collision-{req_hash[:16]}"
                if not L.load(collision_key):  # dedupe: dispose each collision once
                    refuse(L, rid,
                           "ID-COLLISION: request id reused with different content; the "
                           "original line and this line have different "
                           "request_line_sha256 — refusing the conflicting line, original "
                           "disposition unchanged", req_hash,
                           extra={"id_collision": True,
                                  "original_request_line_sha256": prior_hash,
                                  "conflicting_request_line_sha256": req_hash,
                                  "original_status": st.get("status")},
                           key=collision_key)
                continue  # original untouched (still 'started' if it was); its own
                          # line recovers/disposes separately when it reappears
        if st and st.get("status") == "started":
            # --- rev-7 blocker 2 (ChatGPT re-pin-5): before declaring UNPROVEN,
            # inspect the durable RECORD. A record written after a definite
            # spawn-failure (spawn_succeeded False) or after completion proves the
            # outcome even if the crash landed between record and state save — a
            # KNOWN outcome must never degrade to uncertain on restart.
            rec_path = L.record(rid)
            rec = None
            if rec_path.exists():
                try:
                    rec = json.loads(rec_path.read_text())
                except json.JSONDecodeError:
                    rec = None
            if isinstance(rec, dict) and rec.get("spawn_succeeded") is False:
                L.save(rid, "executed", req_hash=req_hash,
                       note="RECOVERED: durable definite spawn-failure record proves "
                            "the process never started; not UNPROVEN")
                log(f"RECOVERED {rid}: definite spawn-failure record before UNPROVEN")
                continue
            if (isinstance(rec, dict) and rec.get("spawn_succeeded") is True
                    and "exit" in rec):
                L.save(rid, "executed", req_hash=req_hash,
                       note="RECOVERED: durable completion record written before the "
                            "crash; outcome certain, not UNPROVEN")
                log(f"RECOVERED {rid}: completion record before UNPROVEN")
                continue
            # outcome genuinely UNCERTAIN after a crash: never re-execute automatically.
            refuse(L, rid,
                   "UNPROVEN: execution was started before a broker restart and its outcome "
                   "is uncertain; re-execution requires a separate explicit owner recovery "
                   "decision (§3.3 rev-5)", req_hash,
                   extra={"unproven": True, "started_note": st.get("note", "")})
            continue
        if st and st.get("status") in ("executed", "dispositioned", "published"):
            continue  # already decided and hash-consistent; publish handles pendings
        argv = req.get("argv")
        own_digest = canonical_sha256(argv) if isinstance(argv, list) else ""
        # --- rev-7 (Claude re-pin-5 REQUIRED): an UNVERIFIABLE plan — absent,
        # unsigned, signature-failed, or structurally broken — is never terminal.
        # Every queued request simply stays pending; a later valid owner signature
        # supersedes. This closes both the out-of-order plan/sig commit window and
        # the push-capable-attacker blacklist vector.
        if plan.get("status") != "valid":
            log(f"PENDING {rid}: plan unverifiable — no disposition written")
            continue
        entry = plan["commands"].get(own_digest)
        if entry is None:
            # A VALID plan that does not contain this digest is a genuine verified
            # denial (§3.3) — refuse on record.
            refuse(L, rid, "digest not in owner-signed open plan (§3.3)", req_hash,
                   extra={
                       "runner_computed_digest": own_digest,
                       "caller_supplied_digest": req.get("command_digest")})
            continue
        # --- rev-6 pre-spawn gates (Claude re-pin-4 conditions 1+2) ---
        # 1) pinned artifact digests verified BEFORE spawn; mismatch = refuse, run nothing.
        art = digest_artifacts(Path(a.repo), entry["artifacts"])
        bad = {k: v for k, v in art.items() if not v["match"]}
        if bad:
            refuse(L, rid, "ARTIFACT-MISMATCH: a plan-referenced artifact differs from "
                           "its owner-pinned sha256 (or is missing) — refusing before "
                           "spawn; nothing executed", req_hash,
                   extra={"artifact_verification": art,
                          "runner_computed_digest": own_digest})
            continue
        # 2) signed use budget. rev-7 keying (Claude re-pin-5): per-COMMAND use key =
        # argv digest + pinned artifacts + max_runs — NOT the whole-plan digest, so a
        # re-sign that only adds commands cannot reset budgets already consumed.
        # rev-7 also takes max(counter, durable-record history): a broker-state wipe
        # cannot reset a budget whose executions are still on record.
        use_key = canonical_sha256([entry["argv"], entry["artifacts"], entry["max_runs"]])
        used = usage_count(L, use_key)
        if isinstance(used, str):
            # rev-7 blocker 3 (ChatGPT re-pin-5): the durable budget file EXISTS but is
            # corrupt/unparseable -> FAIL CLOSED. Never read corrupt state as zero uses;
            # recovery requires explicit owner intervention (delete/repair the file).
            refuse(L, rid, f"BUDGET-STATE-CORRUPT: durable usage state for this signed "
                           f"command is unreadable ({used}) — refusing to execute; "
                           f"corrupt authorization state must never grant runs "
                           f"(fail closed, §3.3 rev-7)", req_hash,
                   extra={"use_key": use_key, "budget_state": used})
            continue
        used = max(used, record_history_count(L, entry["argv"], entry["artifacts"],
                                              entry["max_runs"]))
        if used >= entry["max_runs"]:
            refuse(L, rid, f"BUDGET-EXHAUSTED: this signed command has already been "
                           f"executed {used}/{entry['max_runs']} authorized time(s) "
                           f"(budget keyed per command: argv+artifacts+max_runs, not "
                           f"request id)", req_hash,
                   extra={"runner_computed_digest": own_digest,
                          "use_key": use_key, "used": used,
                          "max_runs": entry["max_runs"]})
            continue
        # execution lifecycle: started BEFORE the subprocess (durable)
        started = now()
        durable_note = f"argv={json.dumps(entry['argv'])}"
        L.save(rid, "started", note=durable_note, req_hash=req_hash)
        err = None
        try:
            cp = subprocess.run(entry["argv"], capture_output=True, text=True,
                                timeout=3600, cwd=a.repo)
            exit_code, stdout, stderr = cp.returncode, cp.stdout, cp.stderr
        except subprocess.TimeoutExpired:
            exit_code, stdout, stderr, err = None, "", "", "TIMEOUT exceeded 3600s"
        except Exception as e:
            # rev-6 (Claude re-pin-4 condition 4) + rev-7 (Claude re-pin-5 residual):
            # ANY exception from the spawn call means the process NEVER STARTED — no
            # side effect is possible — so this is a DEFINITE failure record, not an
            # uncertain 'started' outcome awaiting UNPROVEN on restart. Broadened from
            # OSError so ValueError (NUL byte), IndexError (empty argv) and any future
            # spawn-path error cannot crash the pass after 'started' was written.
            exit_code, stdout, stderr = None, "", ""
            err = f"SPAWN-FAILED ({type(e).__name__}, never executed): {e}"
            durable_write(L.record(rid), {
                "id": rid, "wave": plan["wave"], "plan_digest": plan.get("plan_digest"),
                "signed_by": plan.get("signed_by"),
                "started": started, "ended": now(),
                "request_line_sha256": req_hash, "request_raw": raw,
                "argv": entry["argv"], "runner_computed_digest": own_digest,
                "caller_supplied_digest": req.get("command_digest"),
                "max_runs": entry["max_runs"], "artifact_contract": entry["artifacts"],
                "exit": None, "stdout": "", "stderr": "", "error": err,
                "spawn_succeeded": False,
                "artifact_digests": art})
            L.save(rid, "executed", note="spawn failed; definite failure recorded",
                   req_hash=req_hash)
            log(f"SPAWN-FAILED {rid}: {e}")
            continue
        bump_usage(L, use_key)
        durable_write(L.record(rid), {
            "id": rid, "wave": plan["wave"], "plan_digest": plan.get("plan_digest"),
            "signed_by": plan.get("signed_by"),
            "started": started, "ended": now(),
            "request_line_sha256": req_hash, "request_raw": raw,
            "argv": entry["argv"], "runner_computed_digest": own_digest,
            "caller_supplied_digest": req.get("command_digest"),
            "max_runs": entry["max_runs"], "artifact_contract": entry["artifacts"],
            "exit": exit_code, "stdout": stdout, "stderr": stderr,
            "error": err, "spawn_succeeded": True,
            "artifact_digests": art})
        L.save(rid, "executed", note="record written; publication pending",
               req_hash=req_hash)
        log(f"EXECUTED {rid} exit={exit_code}")

    # ---- publish: copy durable evidence into the worktree, commit, push ----
    pend = L.pending()
    if not pend:
        return 0
    for rid in pend:
        for src, reldir in ((L.record(rid), RECORD_DIR), (L.refusal(rid), REFUSAL_DIR)):
            if src.exists():
                dest = Path(a.repo) / reldir / f"{rid}.json"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(src.read_text())
    paths = [str(Path(a.repo) / d) for d in (RECORD_DIR, REFUSAL_DIR)
             if (Path(a.repo) / d).exists()]
    if not paths:
        return 3
    try:
        git_checked(a.repo, "add", *paths)
        staged = subprocess.run(("git", "-C", a.repo, "diff", "--cached", "--quiet"),
                                capture_output=True, text=True)
        if staged.returncode != 0:  # rc=1 means changes staged — the normal path
            git_checked(a.repo, "commit",
                        "-m", f"broker({a.branch}): {len(pend)} records {now()}")
        git_checked(a.repo, "push", "origin", a.branch)
    except RuntimeError as e:
        log(f"evidence publication FAILED (state kept, will retry): {e}")
        return 3
    for rid in pend:
        st = L.load(rid) or {"id": rid}
        durable_write(L.state(rid), {**st, "status": "published", "updated": now()})
    log(f"published {len(pend)} dispositions (durable, confirmed push)")
    return 0

def main() -> None:
    c = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=c.get("repo", "/opt/m0-broker/evidence"))
    ap.add_argument("--branch", default=c.get("branch", "m0-evidence"))
    ap.add_argument("--poll", type=int, default=c.get("poll", 10))
    ap.add_argument("--state-dir", default=c.get("state_dir", STATE_DEFAULT))
    ap.add_argument("--allowed-signers", default=c.get(
        "allowed_signers", str(Path.home() / ".ssh" / "m0-allowed-signers")))
    ap.add_argument("--owner-principal", default=c.get("owner_principal", ""))
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--daemon", action="store_true", help="loop mode (systemd)")
    mode.add_argument("--once", action="store_true",
                      help="exactly one fetch/process/publish cycle, then exit (default)")
    ap.add_argument("--verify", action="store_true",
                    help="self-check deps and plan-verify path, then exit 0/1")
    a = ap.parse_args()
    allowed_signers = Path(a.allowed_signers)
    L = Ledger(a.state_dir)

    if a.verify:
        problems = []
        if not a.owner_principal:
            problems.append("owner_principal not configured")
        if not allowed_signers.exists():
            problems.append(f"allowed_signers missing: {allowed_signers}")
        if not Path(a.repo).is_dir():
            problems.append(f"evidence repo clone missing: {a.repo}")
        try:
            Path(a.state_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            problems.append(f"state_dir not writable: {a.state_dir} ({e})")
        if Path(a.repo).is_dir():
            v = verify_plan(a.repo, allowed_signers, a.owner_principal)
            if v.get("why", "").startswith("plan signature FAILED"):
                problems.append("plan signature verification path errors")
        for p in problems:
            log(f"VERIFY FAIL: {p}")
        if problems:
            sys.exit(1)
        log("VERIFY OK: config, signer file, repo clone, state dir, verification path")
        return

    if a.daemon:
        push_fails = 0
        while True:
            rc = run_pass(a, allowed_signers, L)
            if rc == 2:
                push_fails += 1
                if push_fails >= PUSH_FAIL_LIMIT:
                    sys.exit(2)   # visible failure; systemd backoff restart
                time.sleep(a.poll * 3)
            elif rc == 3:
                push_fails += 1
                if push_fails >= PUSH_FAIL_LIMIT:
                    sys.exit(3)
                time.sleep(a.poll * 3)
            else:
                push_fails = 0
                time.sleep(a.poll)
    else:
        sys.exit(run_pass(a, allowed_signers, L))

if __name__ == "__main__":
    main()
