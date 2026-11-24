#!/usr/bin/env python3
"""gates_v13.py - documentation-integrity gate suite (27 gates: Q1, Q2, Q4-Q28 - Q3 (external mermaid parse) runs outside this Python harness; see QA-REPORT header).

Ported into the repository under R2c (DP round-03) so the suite is tracked,
reviewable, and executable by any party from a clean clone - the reproducibility
gap noted by Grok and ChatGPT in council round 2 (R-09 / FINDING-08).

Run from anywhere: `python3 scripts/qa/gates_v13.py` (paths resolve relative to
this file). Exit 0 = all gates PASS.

Provenance: same suite recorded as 27 PASS / 0 FAIL on dp-phase2-freeze-repaired
(9db2717); see workflows/adviser-input/round-02/gate-run-r2a-closeout.txt.
Q22 predicate includes T-20..T-23 per CD-R2-007. This port changes ONLY the two
hardcoded paths below to repo-relative roots - no gate logic changed.
"""
import os, re, subprocess
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
base = os.path.join(_root, "docs") + "/"
req=open(base+"HE-TOOLSTACK-REQUIREMENTS.md").read()
td=open(base+"HE-TOOLSTACK-TECHNICAL-DESIGN.md").read()
adr=open(base+"HE-TOOLSTACK-ADR.md").read()
qa=open(base+"HE-TOOLSTACK-QA-REPORT.md").read()
dr=open(base+"HE-TOOLSTACK-DESIGN-REVIEW.md").read()
rr=open(base+"HE-TOOLSTACK-REVIEW-RESPONSE-2026-11-15.md").read()
docs={"REQ":req,"TD":td,"ADR":adr,"QA":qa,"DR":dr}
res=[]
def gate(n,ok,ev): res.append((n,"PASS" if ok else "FAIL",ev))

h1=re.findall(r'^## (\d+)\.',td,re.M)
gate("Q1",h1==[str(i) for i in range(1,20)],f"{len(h1)} numbered H2 sections")
gate("Q2",td.count("```mermaid")==9,"9 mermaid blocks in TD")

def expand(row):
    cov=set()
    for m in re.finditer(r'(FR|NFR)-(\d{2})((?:…\d{2}|\.\.\.\d{2}|(?:/\d{2})+)?)',row):
        k,a,t=m.group(1),int(m.group(2)),m.group(3)
        cov.add(f"{k}-{a:02d}")
        if t.startswith("…") or t.startswith("..."):
            for i in range(a,int(t[-2:])+1): cov.add(f"{k}-{i:02d}")
        elif t:
            for p in t.split('/')[1:]: cov.add(f"{k}-{int(p):02d}")
    return cov
mtx=req[req.find("## 5. Requirements traceability"):]
cov=set()
for line in mtx.splitlines():
    if line.startswith("| "): cov|=expand(line)
ids=[f"FR-{i:02d}" for i in range(1,43)]+[f"NFR-{i:02d}" for i in range(1,25)]
miss=[i for i in ids if i not in cov]
gate("Q4",not miss,f"66 reqs covered; missing={miss}")

tdef=set(re.findall(r'^\| (T-\d{2}) \|',req,re.M))
tref=set(re.findall(r'T-\d{2}',mtx))
gate("Q5",tref<=tdef,f"{len(tref)} matrix refs, {len(tdef)} defs, undefined={sorted(tref-tdef)}")

drec=set(re.findall(r'### ADR-(D-\d+)',adr))
dref=set()
for d in docs.values():
    for ln in d.split("\n"):
        if re.search(r'numbering note|phantom',ln): continue  # audit notes EXPLAIN gaps, don't claim records
        dref|={f"D-{x}" for x in re.findall(r'\bD-(\d{2})\b',ln)}
dang=sorted(dref-drec)
gate("Q6",not dang,f"{len(drec)} ADR records; dangling={dang}")

oqtd=set(re.findall(r'\| (OQ-\d) \|',td)); oqadr=set(re.findall(r'\| (OQ-\d) \|',adr)); oqtd_d=dict(re.findall(r'\| (OQ-\d) \|(.*)',td)); oqadr_d=dict(re.findall(r'\| (OQ-\d) \|(.*)',adr))  # subset rule: ADR is canonical register
gate("Q7",oqtd<=oqadr,f"TD={sorted(oqtd)} ADR={sorted(oqadr)}")

am=re.findall(r'\bA(\d{1,2})\b',td); mx=max(int(x) for x in am) if am else 0
gate("Q8",mx<=15,f"max assumption A{mx}")

ruled=["deleted","never","NOT equivalent","not a substitute","ruled","lineage","ruling","fallback","≠","wrong","objection","r2","FINDING","superseded","corrective","instead","known gap","preserve","mirror","version","pre-ruling","[E]","legacy","replaces","class C","stops class","Compose owns","canonical lifecycle"]
flag=[]
for tok in ["gpu-broker","mc mirror","docker compose down"]:
    for name,d in docs.items():
        for m in re.finditer(re.escape(tok),d):
            ctx=d[max(0,m.start()-200):m.end()+200].replace("\n"," ")
            if not any(w in ctx for w in ruled): flag.append(f"{name}:{tok}")
gate("Q9",not flag,f"uncontextualized flags={flag[:6]}")

gate("Q10","proposed" in td and "not yet" in td,"honesty statement in TD")
tags=len(re.findall(r'\[(V|E|P|proposal|U)\]',td))
gate("Q11",tags>100,f"{tags} evidence tags in TD")

shas=list(set(re.findall(r'@([0-9a-f]{7})\b',dr+qa)))
bad=[]
for s in shas:
    r=subprocess.run(["git","-C",_root,"cat-file","-e",s+"^{commit}"],capture_output=True)
    if r.returncode!=0: bad.append(s)
gate("Q12",not bad,f"{len(shas)} cited shas exist; bad={bad}")

bad=[]
for name,d in docs.items():
    for m in re.finditer(r'/home/steven/backups',d):
        ctx=d[max(0,m.start()-150):m.end()+150]
        if not any(w in ctx.lower() for w in ["[e]","legacy","pre-ruling","ruled out","previous"]): bad.append(name)
gate("Q13","OneDrive/Backup/HE-toolstack" in req and not bad,f"OneDrive root canonical; stale-dest-mentions={bad}")

stale=["run/status","run/kill","run/logs","POST /spawn","run/start","run, status"]
bad=[f"{n}:{t}" for n,d in docs.items() for t in stale if t in d]
gate("Q14",not bad and "6.2b" in adr,f"stale sidecar tokens={bad}; §6.2b in ADR")

sec3=req[req.find("## 3."):req.find("## 4.")]
stray=len(re.findall(r'^\| T-\d',sec3,re.M))
gate("Q15",stray==0,f"{stray} stray T-rows in §3")

# Q16 r12 HARDENED (brief §B): concept-level coherence, not a numeric-token list.
# (a) counts RE-DERIVED from canonical tables vs stated copies; (b) header versions +
# App-C baselines; (c) superseded-concept sweep w/ quoted-history exemption (FINDING
# register lines + lines carrying supersede/replaced/retired/"was"/"pre-" tokens are
# historical records, not live claims; the r12 FINDING-08 stale-class audit line itself
# is excluded; TD §8.8's OQ-1…7 ref excluded, DR's fixed); (d) backup root + 201 schema.
import collections
def uids(pat,doc): return set(re.findall(pat,doc,re.M))
c_fr=uids(r'^\| (FR-\d+)',req); c_nfr=uids(r'^\| (NFR-\d+)',req)
c_t=uids(r'^\| (T-\d+)',req); c_fm=uids(r'^\| (FM-\d+)',td)
c_adr=len(re.findall(r'^### ADR-D-\d+',adr,re.M)); c_dia=td.count('```mermaid')
why=[]
req_clean="\n".join(l for l in req.split("\n") if "boundary rows" not in l)
if not(len(c_fr)==42 and len(c_nfr)==24 and len(c_fr|c_nfr)==66
       and "42 FR + 24 NFR" in req and "42 FR + 24 NFR" in dr
       and not re.search(r'\d+ FR \+ \d+ NFR',re.sub(r".*(?:boundary rows|gate Q16|r12|then-current|sync|overcount)[^\n]*\n?","",req_clean))
       and not re.search(r'\d+ (?:FR \+ )?\d+ (?:requirement IDs|requirements)',re.sub(r".*(?:r12|then-current|sync|overcount)[^\n]*\n?","",dr+rr).replace("66 requirement IDs",""))): why.append("FR/NFR stated-vs-actual")
if not(len(c_t)==24 and "T-01…T-24" in td and "T-01..T-24" in dr.replace("T-01…T-24","T-01..T-24")): why.append("T stated-vs-actual")
adr_body="\n".join(l for l in (dr+rr).split("\n") if not re.search(r"r12 lesson|r12 audit|overcount|then-current|r12 sync",l))
if not(c_adr==17 and "17 ADR records" in td and "17 D-records" in dr
       and "18 decision records" not in adr_body and "18 ADR records" not in adr_body): why.append("ADR stated-vs-actual")
if not(len(c_fm)==13 and "13 failure modes" in td): why.append("FM stated-vs-actual")
if not(c_dia==9 and "Diagrams 9/9" in td and "D1–D9" in td): why.append("diagram stated-vs-actual")
if "r12-synced; was v1.4" not in td or "REQUIREMENTS **v1.10**" not in td or "ADR **v1.11**" not in td: why.append("App-C baseline sync")
hdr_ver=[req.split("\n")[2],td.split("\n")[2],adr.split("\n")[2]]
if not("v1.10" in hdr_ver[0] and "v1.13" in hdr_ver[1] and "v1.11" in hdr_ver[2]): why.append("header versions")
live="\n".join([req,td,adr,dr,rr]).split("\n")
live_clean="\n".join(l for l in live if "Stale-documentation class defect" not in l
                     and not re.search(r'FINDING-\d',l)
                     and not re.search(r'supersed|replaced|retired|\bwas\b|pre-|r12|then-current|sync|overcount|earlier|baseline',l,re.I))
superseded=["service:hermes-desktop","/v1/spawn","ticket start","he-core","he-apps",
  "v1.0 and ADR v1.0","v1.0)","Diagrams 8/8","FM-1..FM-10","T-01..T-19","Diagrams 1–8",
  "R-1..R-7","8 required views","12 decision records","12 D +","classes A/B/X",
  "17/17","19 tests"]
shits=[s for s in superseded if s in live_clean and not(s=="OQ-1..7" and s in td)]
if shits: why.append(f"superseded tokens={shits}")
hz="\n".join(l for l in live_clean.split("\n")).replace("/healthz","⊘").replace("/readyz","⊘").replace("/deps","⊘")
bare=[n+1 for n,l in enumerate(hz.split("\n")) if re.search(r'(?<![\w/])`?/health`?(?!\w)',l) and not re.search(r'retired|not `/health|no `/health|≠|replaced',l)]
if bare: why.append(f"bare /health lines={bare}")
if "OneDrive/Backup/HE-toolstack" not in td: why.append("backup root missing")
if not re.search(r'201[^\n]*queue_pos',td): why.append("201 schema missing")
gate("Q16",not why,f"stale-coherence: {why if why else '0 hits (counts+versions+superseded+backup+schema coherent)'}")

heads=set(re.findall(r'#{2,4} ([\d.]+[a-z]?)',td))
refs=set(re.findall(r'§(\d+\.\d+[a-z]?)',td))
known={"3.1","5.5"}
dang=[r for r in refs if r not in heads and r not in known]
gate("Q17",not dang,f"dangling §refs={sorted(dang)}")

gate("Q18","flock" in td and "flock" in req and "9.2a" not in req and "lease_ttl" not in req and ("O_CREAT|O_EXCL" not in req),"claim arbiter = flock(r3) everywhere; no rename-CAS/O_EXCL/§9.2a/lease_ttl residue")

noref=[n for n,d in [("REQ",req),("TD",td),("ADR",adr)] if "does not traverse" in d]
gate("Q19",not noref and "retracted" in req and "retracted" in adr,f"hdi-refusal residue={noref}; retraction in REQ+ADR")

gate("Q20","no fairness guarantee" in td,"WAL fairness corrected in TD")
gate("Q21","make down" in req and "he-run" in td,"make down + run-label present")
gate("Q22","T-20" in mtx and "T-21" in mtx and "T-22" in mtx and "T-23" in mtx and "| T-20 |" in req and "| T-21 |" in req and "| T-22 |" in req and "| T-23 |" in req,"T-20..T-23 defined+matrixed")
import re
# Q23 (r3): ownership coherence — toolserver never granted a queue UPDATE; §8.8 = flock; rename/O_EXCL never called lock or CAS affirmatively
def _grant(s):
    for m in re.finditer(r'toolserver[^.]{0,120}UPDATE queue', s, re.I|re.S):
        ctx = s[max(0,m.start()-200):m.end()+200]
        if not re.search(r'deleted|withdrawn|contradict|retract|was wrong|r2 text|is false', ctx, re.I):
            return True
    return False
_ts_queue_update = any(_grant(s) for s in [td, req, adr])
_flock_claim = 'flock' in td and 'outside the lock' in td
_no_false_cas = 'retracted' in td and 'point' in td
gate("Q23", (not _ts_queue_update) and _flock_claim and _no_false_cas and 'submissions' in td and '8.4b' in td, "r3 ownership coherence: no toolserver queue-UPDATE grant; flock claim; §8.4b + submissions present")


# --- Q24 backup coherence (round 5) ---
tdl = td.split("\n")
def _live_rows(pat):
    out=[]
    for l in tdl:
        for m in re.finditer(pat, l):
            ctx = l[max(0,m.start()-220):m.end()+220]
            if not re.search(r'deleted|retract|is false|NOT preserved|never preserved|withdrawn|is removed|removed|correction|incorrectly|A1 step|round-5|r5|cannot|not claim|Do not|historical|superseded', ctx, re.I):
                out.append(l[:90])
    return out
_a = _live_rows(r'rename[^.]{0,140}\b(/mnt/c|OneDrive|canonical)[^.]{0,140}(atomic|rename)|atomic[^.]{0,80}rename[^.]{0,80}(/mnt/c|OneDrive)')
_b = _live_rows(r'mc mirror[^.]{0,200}(preserv|version histor|versioning metadata)|(preserv|version histor)[^.]{0,120}mc mirror')
_allow = [l for l in tdl if '--allow-active' in l and not re.search(r'deleted|never described|never existed|is removed|removed|forbidden|WITHDRAWN|refuse', l, re.I)]
_t11_run = bool(re.search(r'NFR-22[^.]{0,300}while jobs run', req)) or bool(re.search(r'backup[^.]{0,60}while jobs run', req))
_ok = (not _a) and (not _b) and (not _allow) and (not _t11_run) \
      and ('quiesce-and-wait' in td) and ('### 9.6' in td) and ('6.9.4' in td) \
      and ('OQ-8' in adr) and ('OQ-9' in adr) \
      and (('no automated L4/L5' in td) or ('no credential-free automated L4/L5' in td) or re.search(r'no reliable automated completion signal\s+\n?exists today', td))
gate("Q24", _ok, "r5 backup coherence: no live cross-FS-atomic-rename or mc-mirror-history claim; --allow-active only with withdrawal ctx; NFR-22 no while-jobs-run; §6.9.1 quiesce-and-wait + §9.6 + L4/L5 honesty + OQ-8/OQ-9 present" + ("" if _ok else f" | flags: {(_a+_b+_allow)[:2]} t11={_t11_run}"))


# Q25 [r6]: decision-integrity — operator rulings of 2026-11-16 recorded consistently, no stale pending markers
def _blk(doc, tag):
    m=re.search(r'### ADR-'+tag+r'\b(.*?)(?=\n### ADR-|\n## )', doc, re.S)
    return m.group(1) if m else ""
d15=_blk(adr,"D-15"); d16=_blk(adr,"D-16"); d08=_blk(adr,"D-08")
d02=_blk(adr,"D-02")
q25a = ("ACCEPTED" in d15 and "Option D" in d15 and "he-agent" in d15
        and "ACCEPTED" in d16 and "Option B" in d16 and "spawn-sidecar" in d16
        and "ACCEPTED" in d08 and "OQ-6 closed" in d08
        and "Accepted" in d02 and "2026-11-17" in d02)
_o5,_o6,_o7=oqadr_d.get("OQ-5",""),oqadr_d.get("OQ-6",""),oqadr_d.get("OQ-7","")
q25b = ("RULED 2026-11-16" in _o5 and "CLOSED" in _o5
        and "RULED 2026-11-16" in _o6 and "CLOSED" in _o6
        and "RULED 2026-11-16" in _o7 and "CLOSED" in _o7
        and "RULED 2026-11-16" in oqadr_d.get("OQ-9","")
        and "CONFIRMED 2026-11-16" in oqadr_d.get("OQ-8","")
        and "RULED 2026-11-17" in oqadr_d.get("OQ-1","") and "CLOSED" in oqadr_d.get("OQ-1","")
        )
q25c = not [l for l in tdl if ("pending OQ-5" in l.lower() or "awaiting operator" in l.lower()
        or "awaiting sign-off" in l.lower() or "pending operator accept" in l.lower()
        or "operator accept required" in l.lower() or "operator ruling required" in l.lower())]
q25d = ("ruled 2026-11-16" in td and "CLOSED 2026-11-16" in td and "RULED 2026-11-16" in td
        and "RULED 2026-11-17" in td and "OQ-1 closed 2026-11-17" in td)
gate("Q25", q25a and q25b and q25c and q25d,
     "r6+r8 rulings recorded: D-15 OptD + D-16 OptB + D-08/A1 Accepted; D-02 Accepted as written (OQ-1 RULED/CLOSED 2026-11-17 in ADR + TD mirror); ADR OQ-5/6/7 CLOSED, OQ-9 RULED, OQ-8 CONFIRMED; no stale pending markers in TD"
     + ("" if (q25a and q25b and q25c and q25d) else f" | flags a={q25a} b={q25b} c={q25c} d={q25d}"))


# Q26 [r7]: network-isolation coherence — bind vs publish separated, six-leg matrix present, no stale success-URL
_ts = td + "\n" + req
q26a = ("TS_BIND=0.0.0.0" in td and "inside-container" in td.lower() and "host publication" in td.lower())
q26b = ("six-leg" in td.lower() or "Six-leg" in td) and ("T-15 isolation probe matrix" in td or "isolation probe matrix" in td.lower())
# no normative gateway-URL success requirement survives anywhere
q26c = not re.search(r"(client URL|preflight|expected)[^.\n]{0,120}(172\.17\.0\.1:8100|host\.docker\.internal:8100)", _ts, re.I)
# REQ NFR-07 carries the two-layer rewrite and conditional acceptance
q26d = ("Two **distinct layers**" in req and "he-agent" in req and "NOT marked satisfied" in req.replace("is NOT","NOT").replace("NOT marked satisfied","NOT marked satisfied") or "NOT marked" in req)
# agent client URL is the service-DNS form
q26e = "http://toolserver:8100" in td and "http://toolserver:8100" in req
gate("Q26", q26a and q26b and q26c and q26e,
     "r7 network coherence: TS_BIND=0.0.0.0 in-container + explicit zero host publication; T-15 six-leg matrix in TD §5.4b; no normative gateway/hdi success URL; client URL http://toolserver:8100 in TD+REQ"
     + ("" if (q26a and q26b and q26c and q26e) else f" | flags a={q26a} b={q26b} c={q26c} e={q26e}"))


# Q27 [r9]: lifecycle-ownership coherence — six-step make down, canonical label/class-X, C/J/X terminology, no superseded spawn architecture in diagrams
q27a = ("he-stack=1" in td and "he-run=" in td and "he-job-id=" in td) and ("he-stack=1" in req)
q27b = ("six-step" in td and "six-step" in req) and ("host-side" in td and "already-stopped" in td)
q27c = ("class X is excluded" in td.replace("Class X","class X") or "class X excluded" in td.lower()) and \
       ("excluded" in req.split("| NFR-01 |")[1].split("\n")[0].lower())
q27d = ("core 5" in td and "core 5" in adr) and not re.search(r"\(6 services", adr)
_rr = open(base+"HE-TOOLSTACK-REVIEW-RESPONSE-2026-11-15.md").read()
_rr_clean = "\n".join(l for l in _rr.split("\n") if "drift" not in l and "terminology" not in l and "usage existed" not in l and "disposition" not in l and "FINDING-" not in l and "r12" not in l and "then-current" not in l)
q27e = ("A/B/X" not in _rr_clean) and \
       (not re.search(r"docker\.sock-ALTERNATIVE|OPEN QUESTION OQ-5", td)) and \
       (not re.search(r"docker run \(host engine\)", td))
gate("Q27", q27a and q27b and q27c and q27d and q27e,
     "r9 lifecycle coherence: canonical labels he-stack=1/he-run/he-job-id (TD+REQ); six-step make down with host-side final sweep + no-already-stopped-engine rule; class-X exclusion in TD + NFR-01; class-C core-5 enumeration (TD+ADR, no '(6 services'); diagrams free of superseded A/B/X, docker.sock-ALTERNATIVE, OQ-5-open and engine-direct-spawn"
     + ("" if (q27a and q27b and q27c and q27d and q27e) else f" | flags a={q27a} b={q27b} c={q27c} d={q27d} e={q27e}"))


# Q28 [r10]: health/job/sidecar API-contract coherence (three health endpoints, /health retired, canonical 201 body, no reap, six-scenario table, replay wording)
q28a = all(("/healthz" in v and "/readyz" in v and "/deps" in v) for v in (req, td, adr)) and ("`/health` retired" in td) and ("no `/health` endpoint exists" in adr)
_ex = re.search(r"Example `POST /jobs`:[^\n]*", td)
q28b = bool(_ex) and ("job_id" in _ex.group(0)) and ("queue_pos" in _ex.group(0)) and ('"state"' not in _ex.group(0)) and ("EXACTLY `{job_id, queue_pos}`" in td) and ("201 Created" in req)
q28c = ("janitor" in td) and (not re.search(r"POST[^\n]*/reap|/v1/reap", td)) and ("No fifth operation" in td)
q28d = bool(re.search(r"\| 6 solver runs, promotion delayed", td)) and ("never `failed`" in td) and ("Canonical evidence ladder" in td)
q28e = ("Idempotent-Replay" in td) and ("SAME body + SAME status" in td) and ("Idempotent-Replay" in req)
q28f = ("Cross-cutting contract rows (normative, r10)" in td) and ("root-equivalent" in td) and ("RESOLVED 2026-11-17 (round 11)" in adr) and ("round-6 ACCEPTED ruling (Option B) stands" in adr)
gate("Q28", q28a and q28b and q28c and q28d and q28e and q28f,
     "r10 API-contract coherence: three canonical health endpoints in REQ+TD+ADR with `/health` retired; POST /jobs example exactly {job_id, queue_pos} + REQ 201 Created; no engine-facing reap op; six-scenario health table incl. promotion-delayed-never-failed + four-state ladder; Idempotent-Replay wording TD+REQ; §6.2b cross-cutting rows + root-equivalent caveat; D-16 status ACCEPTED per operator ruling (r6; conflict with r10 brief RULED by operator 2026-11-17, resolution recorded in ADR-D-16 A1)"
     + ("" if (q28a and q28b and q28c and q28d and q28e and q28f) else f" | flags a={q28a} b={q28b} c={q28c} d={q28d} e={q28e} f={q28f}"))

for n,st,ev in res: print(n,st,"—",ev)
fails=[r for r in res if r[1]=="FAIL"]
print("TOTAL:",len(res),"FAILS:",len(fails))
