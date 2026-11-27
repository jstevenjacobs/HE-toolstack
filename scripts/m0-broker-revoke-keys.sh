#!/usr/bin/env bash
# m0-broker-revoke-keys.sh — §3.1 cutover key surgery, SELECTIVE by fingerprint
# (rev-6; repairs ChatGPT re-pin-4 findings 2 + 4 on top of rev-5's selectivity).
#
# Usage:
#   revoke mode:  M0_REVOKE_FPR="SHA256:aa.. SHA256:bb.." \
#                 M0_RECOVERY=local-console|keep:<SHA256:..> \
#                 [M0_INVENTORY=<inventory file>] \
#                 m0-broker-revoke-keys.sh --revoke <authorized_keys files...>
#   verify mode:  m0-broker-revoke-keys.sh --verify <inventory file> \
#                 <authorized_keys files...>
#
# rev-6 rules (ChatGPT re-pin-4):
#  1. STRICT recovery declaration (repair 2): M0_RECOVERY must be exactly
#     'local-console' or 'keep:<SHA256:...>'. ANY other value — including the
#     old protocol's 'recovery:<fpr>' form, which is hereby REMOVED from the
#     protocol — is an unrecognized declaration and the script REFUSES. An
#     unrecognized declaration must never silently become a local-console claim.
#  2. INVENTORY-WIDE expected-state verification (repair 4): when M0_INVENTORY
#     points at the pre-cutover inventory (the file m0-broker-setup.sh writes),
#     EVERY fingerprint in it gets an expected state — ABSENT for every revoked
#     Hermes credential, PRESENT for every non-revoked credential — each is
#     re-probed individually against the live files, and ANY unexpected state
#     exits non-zero. The owner never infers completeness from a subset.
#  3. One CONSOLIDATED verification record: $CUTOVER_DIR/cutover-verification.txt
#     carries one line per credential: "<file-or-GLOBAL> <fpr> EXPECTED=.. OBSERVED=.. OK|FAIL".
#  4. Only fingerprints explicitly listed in M0_REVOKE_FPR are removed; every
#     modified file gets a timestamped backup; the retained recovery fingerprint
#     may not appear in the revoke list.
#  5. --verify is the same expected-state enforcement standalone (exit non-zero
#     on any unexpected state; rev-5's print-only mode is retired).
set -euo pipefail
CUTOVER_DIR="${CUTOVER_DIR:-/opt/m0-broker/cutover}"
MODE="${1:?usage: --revoke|--verify ...}"; shift

fpr_of_line() {  # fingerprint of one authorized_keys line, "" on parse failure
  local out
  out=$(printf '%s\n' "$1" | ssh-keygen -lf - 2>/dev/null | awk '{print $2}') || true
  echo "${out:-}"
}

# is_revoked <fpr> -> 0 if in revoke list
is_revoked() {
  local f
  for f in "${REV[@]}"; do [[ $f == "$1" ]] && return 0; done
  return 1
}

# verify_inventory <verification-file>: every fpr in the inventory gets an
# expected state, each re-probed live, consolidated lines, FAIL flag on any
# mismatch. Returns 1 on any unexpected state.
verify_inventory() {
  local vfile="$1" INV_FPRS=() hk line fp found expected observed
  while read -r _ rest; do
    fp=$(printf '%s' "$rest" | awk '{print $2}')
    [[ -z $fp || $fp != SHA256:* ]] && continue
    INV_FPRS+=("$fp")
  done < "$INV"
  [[ ${#INV_FPRS[@]} -gt 0 ]] || { echo "REFUSE: inventory file yielded no fingerprints" >&2; return 1; }
  local FAIL=0
  for fp in "${INV_FPRS[@]}"; do
    if is_revoked "$fp"; then expected=ABSENT; else expected=PRESENT; fi
    found=""
    for hk in "${FILES[@]}"; do
      [[ -f $hk ]] || continue
      while IFS= read -r line; do
        [[ -z ${line// /} ]] && continue
        [[ $(fpr_of_line "$line") == "$fp" ]] && found=yes
      done < "$hk"
    done
    observed=$( [[ -n $found ]] && echo PRESENT || echo ABSENT )
    if [[ $expected == "$observed" ]]; then
      echo "INVENTORY $fp EXPECTED=$expected OBSERVED=$observed OK" >> "$vfile"
    else
      echo "INVENTORY $fp EXPECTED=$expected OBSERVED=$observed FAIL" >> "$vfile"; FAIL=1
    fi
  done
  return $FAIL
}

if [[ $MODE == --revoke ]]; then
  FILES=("$@")
  [[ ${#FILES[@]} -gt 0 ]] || { echo "no authorized_keys files given"; exit 1; }
  REVOKE_STR="${M0_REVOKE_FPR:-}"
  RECOVERY="${M0_RECOVERY:-}"
  INV="${M0_INVENTORY:-}"
  [[ -n $REVOKE_STR ]] || { echo "REFUSE: M0_REVOKE_FPR empty — selective revocation requires explicit fingerprints"; exit 1; }
  [[ -n $RECOVERY ]] || { echo "REFUSE: M0_RECOVERY unset — declare 'local-console' or keep:<SHA256:fpr>"; exit 1; }
  read -ra REV <<< "$REVOKE_STR"
  KEEP_FPR=""
  case "$RECOVERY" in
    local-console) : ;;
    keep:*)
      KEEP_FPR="${RECOVERY#keep:}"
      [[ $KEEP_FPR == SHA256:* ]] || { echo "REFUSE: keep: declaration is not a SHA256: fingerprint"; exit 1; }
      for f in "${REV[@]}"; do
        [[ $f == "$KEEP_FPR" ]] && { echo "REFUSE: recovery fingerprint is also in the revoke list"; exit 1; }
      done
      ;;
    *)
      # rev-6 repair 2: unknown forms (the removed recovery:<fpr> included) must
      # NOT fall through to an implicit local-console assertion.
      echo "REFUSE: unrecognized M0_RECOVERY '$RECOVERY' — allowed: local-console | keep:<SHA256:fpr> (recovery:<fpr> was removed from §3.1 in rev-6)"
      exit 1
      ;;
  esac
  [[ -n $INV ]] || { echo "REFUSE: M0_INVENTORY unset — revocation must state the FULL credential inventory or inventory-wide completeness can never be proven (rev-7, ChatGPT re-pin-5 P1; was WARN+proceed in rev-6)"; exit 1; }
  [[ -f $INV ]] || { echo "REFUSE: M0_INVENTORY set but file missing"; exit 1; }
  mkdir -p "$CUTOVER_DIR/backup"
  STAMP=$(date -u +%Y%m%dT%H%M%SZ)
  for hk in "${FILES[@]}"; do
    [[ -f $hk ]] || continue
    cp -p "$hk" "$CUTOVER_DIR/backup/${hk//\//_}.$STAMP"
    : > "$hk.tmp"
    while IFS= read -r line; do
      [[ -z ${line// /} ]] && continue
      fp=$(fpr_of_line "$line")
      drop=0
      for f in "${REV[@]}"; do [[ -n $fp && $fp == "$f" ]] && drop=1; done
      [[ $drop -eq 0 ]] && printf '%s\n' "$line" >> "$hk.tmp"
    done < "$hk"
    mv "$hk.tmp" "$hk"
  done
  # ---- consolidated verification record (rev-6) ----
  VF="$CUTOVER_DIR/cutover-verification.txt"
  : > "$VF"
  echo "# cutover verification (rev-6) $STAMP" >> "$VF"
  echo "# files: ${FILES[*]}" >> "$VF"
  echo "# revoke list: $REVOKE_STR" >> "$VF"
  echo "# recovery: $RECOVERY" >> "$VF"
  FAIL=0
  # (a) explicit revoke list: every entry ABSENT everywhere
  for f in "${REV[@]}"; do
    found=""
    for hk in "${FILES[@]}"; do
      [[ -f $hk ]] || continue
      while IFS= read -r line; do
        [[ $(fpr_of_line "$line") == "$f" ]] && found=yes
      done < "$hk"
    done
    observed=$( [[ -z $found ]] && echo ABSENT || echo PRESENT )
    if [[ $observed == ABSENT ]]; then
      echo "REVOKE $f EXPECTED=ABSENT OBSERVED=ABSENT OK" >> "$VF"
    else
      echo "REVOKE $f EXPECTED=ABSENT OBSERVED=PRESENT FAIL" >> "$VF"; FAIL=1
    fi
  done
  # (b) retained recovery key PRESENT somewhere
  if [[ -n $KEEP_FPR ]]; then
    found=""
    for hk in "${FILES[@]}"; do
      [[ -f $hk ]] || continue
      while IFS= read -r line; do
        [[ $(fpr_of_line "$line") == "$KEEP_FPR" ]] && found=yes
      done < "$hk"
    done
    observed=$( [[ -n $found ]] && echo PRESENT || echo ABSENT )
    if [[ $observed == PRESENT ]]; then
      echo "RECOVERY $KEEP_FPR EXPECTED=PRESENT OBSERVED=PRESENT OK" >> "$VF"
    else
      echo "RECOVERY $KEEP_FPR EXPECTED=PRESENT OBSERVED=ABSENT FAIL (OWNER RECOVERY LOST)" >> "$VF"; FAIL=1
    fi
  else
    echo "RECOVERY local-console EXPECTED=attested OBSERVED=attested OK (owner attests local access; no SSH recovery key claimed)" >> "$VF"
  fi
  # (c) INVENTORY-WIDE expected states (rev-6 repair 4): every inventoried
  # credential — including container-side copies if their files are in FILES.
  if [[ -n $INV ]]; then
    echo "# inventory: $INV" >> "$VF"
    verify_inventory "$VF" || FAIL=1
  else
    echo "INVENTORY none EXPECTED=n/a OBSERVED=n/a WARN (M0_INVENTORY unset: inventory-wide completeness NOT proven)" >> "$VF"
    FAIL=1   # rev-6: an incomplete verification is a failed verification
  fi
  cat "$VF"
  [[ $FAIL -eq 0 ]] || { echo "CUTOVER VERIFICATION FAILED — do not declare revocation"; exit 1; }
  echo "Cutover key surgery verified: every inventoried credential checked against its expected state."
  exit 0
fi

if [[ $MODE == --verify ]]; then
  INV="${1:?usage: --verify <inventory-file> <authorized_keys files...>}"; shift
  FILES=("$@")
  [[ -f $INV ]] || { echo "REFUSE: inventory file missing: $INV"; exit 1; }
  [[ ${#FILES[@]} -gt 0 ]] || { echo "no authorized_keys files given"; exit 1; }
  # standalone mode assumes the inventory holds ONLY already-revoked creds unless
  # M0_REVOKE_FPR says otherwise; kept consistent with revoke expectations.
  read -ra REV <<< "${M0_REVOKE_FPR:-}"
  VF="${CUTOVER_DIR:-/tmp}/cutover-verify-standalone.txt"
  mkdir -p "${CUTOVER_DIR:-/tmp}"
  : > "$VF"
  if verify_inventory "$VF"; then cat "$VF"; exit 0; else cat "$VF"; exit 1; fi
fi
echo "unknown mode: $MODE"; exit 1
