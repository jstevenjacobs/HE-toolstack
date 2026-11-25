#!/usr/bin/env bash
# m0-broker-setup.sh — M0 interview protocol §3.1 broker provisioning (DRAFT — not yet executed).
#
# Owner-runs-with-own-hands script (protocol §3.1). Hermes prepares it; the owner reads
# it fully, then runs it. Two explicit phases so a misconfigured broker can never strand
# execution authority:
#   phase 1 (default): PROVISION the broker; touches nothing Hermes depends on.
#   phase 2 (--confirm-cutover): REVOKE Hermes's host SSH access — the point of no
#           casual return. Run ONLY after the phase-1 health checks pass.
#
# This file is committed for review at the rev-3 pin. Nothing it describes is in effect
# until the protocol is council-ACCEPTED and the owner executes it during Wave 0.
set -euo pipefail

BROKER_USER="m0broker"
EVIDENCE_REPO="git@github.com:jstevenjacobs/HE-toolstack.git"   # broker branch: m0-evidence
BROKER_BRANCH="m0-evidence"
HERMES_SSH_KEY_FINGERPRINTS_FILE="/etc/m0/hermes-revoked-keys.txt"   # created by phase 1 from current authorized_keys entries named by owner
PHASE="${1:-provision}"

if [[ $EUID -ne 0 ]]; then echo "run as: sudo ./m0-broker-setup.sh [provision|--confirm-cutover]" >&2; exit 1; fi

if [[ "$PHASE" == "provision" ]]; then
  echo "== PHASE 1: PROVISION (does not touch Hermes's access) =="

  # 1. broker account: no sudo, shell-capable, own group + docker group only
  id -u "$BROKER_USER" &>/dev/null || useradd -m -s /bin/bash -G docker "$BROKER_USER"
  echo "   user $BROKER_USER: $(id "$BROKER_USER")"

  # 2. broker private key (generated HERE; never leaves this host, never enters the Hermes container).
  #    Owner must register the printed PUBLIC half as a deploy key with write access on the
  #    evidence repo (Settings -> Deploy keys) BEFORE phase 2.
  if [[ ! -f /home/$BROKER_USER/.ssh/id_ed25519 ]]; then
    sudo -u "$BROKER_USER" ssh-keygen -t ed25519 -N "" -f /home/$BROKER_USER/.ssh/id_ed25519 -C "m0broker@$(hostname)"
  fi
  echo "   REGISTER THIS as repo deploy key (write): "
  sudo -u "$BROKER_USER" cat /home/$BROKER_USER/.ssh/id_ed25519.pub

  # 3. broker clone + runner unit (polls the request queue branch; executes plan-listed
  #    digests only; pushes full capture records). Runner source lives in the repo at
  #    scripts/m0-broker-runner.py — installed to the broker home below.
  sudo -u "$BROKER_USER" git clone --branch "$BROKER_BRANCH" "$EVIDENCE_REPO" /home/$BROKER_USER/evidence 2>/dev/null || true
  install -m 0755 "$(dirname "$0")/m0-broker-runner.py" /home/$BROKER_USER/m0-broker-runner.py
  cat >/etc/systemd/system/m0-broker.service <<EOF
[Unit]
Description=M0 plan-gated execution broker (protocol §3)
After=network-online.target
[Service]
User=$BROKER_USER
ExecStart=/usr/bin/python3 /home/$BROKER_USER/m0-broker-runner.py --repo /home/$BROKER_USER/evidence --branch $BROKER_BRANCH
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  echo "   unit installed. Start it ONLY after the deploy key is registered:"
  echo "   sudo systemctl enable --now m0-broker && systemctl status m0-broker --no-pager"

  # 4. record (do not yet remove) the Hermes keys currently authorized on this host,
  #    so phase 2 revokes exactly the named fingerprints.
  mkdir -p /etc/m0
  : >"$HERMES_SSH_KEY_FINGERPRINTS_FILE"
  for f in /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys; do
    [[ -f "$f" ]] || continue
    while read -r line; do
      [[ -z "$line" ]] && continue
      if printf '%s\n' "$line" | grep -qiE "hermes|host_ed25519"; then
        fp=$(printf '%s\n' "$line" | ssh-keygen -lf - 2>/dev/null | awk '{print $2}')
        [[ -n "$fp" ]] && echo "$fp" >>"$HERMES_SSH_KEY_FINGERPRINTS_FILE"
      fi
    done <"$f"
  done
  sort -u "$HERMES_SSH_KEY_FINGERPRINTS_FILE" -o "$HERMES_SSH_KEY_FINGERPRINTS_FILE"
  echo "   Hermes keys matched for revocation (verify/edit this file before phase 2):"
  cat "$HERMES_SSH_KEY_FINGERPRINTS_FILE"
  echo "   file: $HERMES_SSH_KEY_FINGERPRINTS_FILE"

  echo
  echo "== PHASE 1 DONE. Health-check before cutover =="
  echo "   systemctl is-active m0-broker                         -> active"
  echo "   sudo -u $BROKER_USER git -C /home/$BROKER_USER/evidence push --dry-run  -> ok"
  echo "   a test out-of-plan request -> refusal record appears on $BROKER_BRANCH"
  echo "When all three pass, re-run:  sudo ./m0-broker-setup.sh --confirm-cutover"
  exit 0
fi

if [[ "$PHASE" == "--confirm-cutover" ]]; then
  echo "== PHASE 2: CUTOVER — revokes Hermes's host SSH access (protocol §3.1/§3.6) =="
  if ! systemctl is-active --quiet m0-broker; then
    echo "ABORT: broker unit is not active. Fix phase 1 first — do not strand execution authority." >&2; exit 1
  fi
  echo "Broker is active. In 10 seconds this removes the named Hermes keys from every"
  echo "authorized_keys on this host. Hermes cannot execute on this host afterwards."
  sleep 10
  # Revocation: remove entries whose fingerprints the owner listed at provisioning time.
  # Implemented as an explicit, printed edit per file so the owner sees exactly what disappears.
  while IFS= read -r fp; do
    [[ -z "$fp" || "$fp" == \#* ]] && continue
    echo "  revoking fingerprint: $fp"
    # ssh-keygen -lf resolves to the key line; strip matching lines from every authorized_keys
    for f in /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys; do
      [[ -f "$f" ]] || continue
      while read -r line; do
        if [[ -n "$line" ]] && printf '%s\n' "$line" | ssh-keygen -lf - 2>/dev/null | grep -qF "${fp##* }"; then
          grep -vF "$line" "$f" >"$f.tmp" && mv "$f.tmp" "$f"
          echo "    removed from $f"
        fi
      done <"$f"
    done
  done <"$HERMES_SSH_KEY_FINGERPRINTS_FILE"
  echo "== CUTOVER DONE. §3.6 bypass-detection test (protocol) must run next; until it passes,"
  echo "   capture completeness is UNPROVEN and no evidence row binds. =="
  exit 0
fi

echo "usage: $0 [provision | --confirm-cutover]" >&2; exit 1
