#!/usr/bin/env bash
# m0-broker-revoke-keys.sh — §3.1 cutover key surgery, SELective by fingerprint
# (rev-5 repair of ChatGPT re-pin-3 finding 4A/4B: rev-4 emptied ALL authorized_keys,
# which could destroy the owner's own recovery access).
#
# Usage:
#   revoke mode:    M0_REVOKE_FPR="SHA256:aa.. SHA256:bb.." \
#                   M0_RECOVERY=local-console|keep:<SHA256:..> \
#                   m0-broker-revoke-keys.sh --revoke <authorized_keys files...>
#   verify mode:    m0-broker-revoke-keys.sh --verify <inventory file> \
#                   <authorized_keys files...>
#
# Rules:
#  - Only fingerprints explicitly listed in M0_REVOKE_FPR are removed.
#  - M0_RECOVERY must be set: either 'local-console' (owner has physical/WSL local
#    access and does not need any SSH key) or keep:<fingerprint> naming one
#    retained owner recovery credential. Refuses to run otherwise.
#  - Every modified file gets a timestamped backup under $CUTOVER_DIR/backup/.
#  - Every fingerprint gets its own line in $CUTOVER_DIR/cutover-verification.txt:
#    revoked fingerprints ABSENT, retained fingerprint PRESENT (rev-5 per-credential
#    verification record; any unverified credential = failure exit).
#  - --verify re-checks an inventory file (from the pre-cutover listing) against
#    the live files and prints per-fingerprint PRESENT/ABSENT results.
set -euo pipefail
CUTOVER_DIR="${CUTOVER_DIR:-/opt/m0-broker/cutover}"
MODE="${1:?usage: --revoke|--verify ...}"; shift

fpr_of_line() {  # fingerprint of one authorized_keys line, "" on parse failure
  local out
  out=$(printf '%s\n' "$1" | ssh-keygen -lf - 2>/dev/null | awk '{print $2}') || true
  echo "${out:-}"
}

if [[ $MODE == --revoke ]]; then
  FILES=("$@")
  [[ ${#FILES[@]} -gt 0 ]] || { echo "no authorized_keys files given"; exit 1; }
  REVOKE_STR="${M0_REVOKE_FPR:-}"
  RECOVERY="${M0_RECOVERY:-}"
  [[ -n $REVOKE_STR ]] || { echo "REFUSE: M0_REVOKE_FPR empty — selective revocation requires explicit fingerprints"; exit 1; }
  [[ -n $RECOVERY ]] || { echo "REFUSE: M0_RECOVERY unset — declare 'local-console' or keep:<SHA256:fpr> for owner recovery access"; exit 1; }
  read -ra REV <<< "$REVOKE_STR"
  KEEP_FPR=""
  if [[ $RECOVERY == keep:* ]]; then
    KEEP_FPR="${RECOVERY#keep:}"
    for f in "${REV[@]}"; do
      [[ $f == "$KEEP_FPR" ]] && { echo "REFUSE: recovery fingerprint is also in the revoke list"; exit 1; }
    done
  fi
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
  # per-credential verification, host side: every revoked fpr ABSENT everywhere;
  # retained recovery fpr PRESENT somewhere.
  : > "$CUTOVER_DIR/cutover-verification.txt"
  FAIL=0
  for f in "${REV[@]}"; do
    found=""
    for hk in "${FILES[@]}"; do
      [[ -f $hk ]] || continue
      while IFS= read -r line; do
        fp=$(fpr_of_line "$line")
        [[ -n $fp && $fp == "$f" ]] && found=yes
      done < "$hk"
    done
    if [[ -z $found ]]; then
      echo "$f ABSENT (revoked OK)" >> "$CUTOVER_DIR/cutover-verification.txt"
    else
      echo "$f STILL-PRESENT (REVOCATION FAILED)" >> "$CUTOVER_DIR/cutover-verification.txt"; FAIL=1
    fi
  done
  if [[ -n $KEEP_FPR ]]; then
    found=""
    for hk in "${FILES[@]}"; do
      [[ -f $hk ]] || continue
      while IFS= read -r line; do
        fp=$(fpr_of_line "$line")
        [[ -n $fp && $fp == "$KEEP_FPR" ]] && found=yes
      done < "$hk"
    done
    if [[ -n $found ]]; then
      echo "$KEEP_FPR PRESENT (owner recovery retained OK)" >> "$CUTOVER_DIR/cutover-verification.txt"
    else
      echo "$KEEP_FPR MISSING (OWNER RECOVERY LOST)" >> "$CUTOVER_DIR/cutover-verification.txt"; FAIL=1
    fi
  else
    echo "recovery=local-console (no SSH recovery key claimed; owner attests local access)" >> "$CUTOVER_DIR/cutover-verification.txt"
  fi
  cat "$CUTOVER_DIR/cutover-verification.txt"
  [[ $FAIL -eq 0 ]] || { echo "CUTOVER VERIFICATION FAILED — do not declare revocation"; exit 1; }
  echo "Cutover key surgery verified per credential."
  exit 0
fi

if [[ $MODE == --verify ]]; then
  INV="${1:?usage: --verify <inventory-file> <authorized_keys files...>}"; shift
  while read -r _ rest; do
    fp=$(echo "$rest" | awk '{print $2}')
    [[ -z $fp || $fp != SHA256:* ]] && continue
    found=""
    for hk in "$@"; do
      [[ -f $hk ]] || continue
      while IFS= read -r line; do
        [[ $(fpr_of_line "$line") == "$fp" ]] && found=yes
      done < "$hk"
    done
    echo "$fp $( [[ -n $found ]] && echo PRESENT || echo ABSENT )"
  done < "$INV"
  exit 0
fi
echo "unknown mode: $MODE"; exit 1
