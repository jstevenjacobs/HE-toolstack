#!/usr/bin/env bash
# m0-broker-setup.sh — M0 interview protocol §3.1: owner runs this ONCE, with own
# hands, on the host (JSJ-Office). Hermes prepares drafts; running it is an owned
# act. Phase 1 provisions; --confirm-cutover (phase 2) revokes Hermes's host
# execution paths ONLY after the health checks pass. Abort between phases leaves
# Hermes working and the broker idle — recoverable, non-destructive.
#
# Rev-4 repairs (ChatGPT re-pin-2 §3B/§5 P0):
#  - Docker group membership asserted (id -nG check) for a pre-existing account.
#  - The script starts + enables the service itself; cutover requires it active.
#  - Counted invocations stated honestly (see usage).
# Rev-5 repairs (ChatGPT re-pin-3 §2 repair 4):
#  - Revocation is SELECTIVE by explicit fingerprint list (M0_REVOKE_FPR), never a
#    blanket authorized_keys wipe; owner declares recovery (M0_RECOVERY) or the
#    script refuses. Timestamped backups of every modified file.
#  - Per-credential verification records written to cutover-verification.txt;
#    any unverified credential aborts the cutover (exit 1).
set -euo pipefail
REPO="${1:?usage: sudo ./m0-broker-setup.sh <repo-checkout-path> [--confirm-cutover]}"
PHASE="${2:-provision}"
BROKER=m0broker
EVID="${EVIDENCE_REMOTE:-git@github.com:jstevenjacobs/HE-toolstack-evidence.git}"

[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }
[[ -d $REPO/.git ]] || { echo "not a git repo: $REPO"; exit 1; }

if [[ $PHASE == --confirm-cutover ]]; then
  # ---- phase 2: verify, then revoke -------------------------------------------
  # HARD gate: broker service must be installed AND active AND runner healthy.
  systemctl is-active --quiet m0-broker || { echo "ABORT: m0-broker service not active (run phase 1 fully first)"; exit 1; }
  install -m 0750 -d -o "$BROKER" -g "$BROKER" /opt/m0-broker/plans /opt/m0-broker/requests \
    /opt/m0-broker/results /opt/m0-broker/inbox /opt/m0-broker/log /opt/m0-broker/tmp
  sudo -u "$BROKER" /usr/bin/python3 /opt/m0-broker/runner.py --verify || {
    echo "ABORT: broker self-verify failed — Hermes keeps access until it passes"; exit 1; }
  # HARD gate: Docker group membership proven for the account actually running.
  id -nG "$BROKER" | grep -qw docker || { echo "ABORT: $BROKER lacks docker group"; exit 1; }
  # Owner-visible revocation ledger: every credential in every authorized_keys.
  mkdir -p /opt/m0-broker/cutover
  : > /opt/m0-broker/cutover/hermes-credentials.txt
  for hk in /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys; do
    [[ -f $hk ]] || continue
    ssh-keygen -lf "$hk" 2>/dev/null | sed "s#^#$hk  #" \
      >> /opt/m0-broker/cutover/hermes-credentials.txt || true
  done
  echo "=== ALL host SSH credentials (review, then re-run to confirm) ==="
  cat /opt/m0-broker/cutover/hermes-credentials.txt
  if [[ ${M0_CUTOVER_CONFIRMED:-} != yes ]]; then
    echo "Re-run as: sudo M0_CUTOVER_CONFIRMED=yes $0 $REPO --confirm-cutover"
    echo "(nothing revoked yet)"
    exit 2
  fi
  # rev-5: SELECTIVE revocation by explicit fingerprint list (ChatGPT re-pin-3 4A:
  # rev-4's blanket ':>' could destroy owner/admin recovery access). The owner must
  # enumerate exactly which fingerprints are Hermes's, and declare how owner access
  # survives: M0_RECOVERY=local-console or M0_RECOVERY=keep:<SHA256:fingerprint>.
  [[ -n ${M0_REVOKE_FPR:-} ]] || { echo "ABORT: set M0_REVOKE_FPR='SHA256:.. SHA256:..' (space-separated Hermes fingerprints from the inventory above)"; exit 1; }
  [[ -n ${M0_RECOVERY:-} ]] || { echo "ABORT: set M0_RECOVERY=local-console  (or keep:<SHA256:fpr> to retain one owner recovery key)"; exit 1; }
  install -m 0755 "$REPO/scripts/m0-broker-revoke-keys.sh" /opt/m0-broker/revoke-keys.sh
  M0_REVOKE_FPR="$M0_REVOKE_FPR" M0_RECOVERY="$M0_RECOVERY" CUTOVER_DIR=/opt/m0-broker/cutover \
    /opt/m0-broker/revoke-keys.sh --revoke \
      /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys \
    || { echo "ABORT: per-credential revocation verification FAILED — fix, do not proceed"; exit 1; }
  # Revocation PROVEN per credential (host side). Container-side re-probe:
  echo "Cutover done. BEFORE declaring Wave-0 ready, PROVE it from the container:"
  echo "  for EACH inventoried Hermes fingerprint: ssh -k <that key> -p 2222 steven@host.docker.internal  =>  MUST be refused"
  echo "  record each result separately in the wave pack; any unverified credential = cutover failure."
  echo "and run §3.6 tests (a)-(d). Until proven, revocation is UNPROVEN."
  exit 0
fi

# ---- phase 1: provision --------------------------------------------------------
install -m 0750 -d -o "$BROKER" -g "$BROKER" /opt/m0-broker/{plans,requests,results,inbox,log,tmp}
install -m 0755 "$REPO/scripts/m0-broker-runner.py" /opt/m0-broker/runner.py
# Broker's own git identity + evidence key.
if [[ ! -f /home/$BROKER/.ssh/id_ed25519 ]]; then
  install -d -m 0700 -o "$BROKER" -g "$BROKER" /home/$BROKER/.ssh
  sudo -u "$BROKER" ssh-keygen -q -t ed25519 -N '' -f /home/$BROKER/.ssh/id_ed25519 \
    -C 'm0-broker@JSJ-Office'
  sudo -u "$BROKER" git config --global user.name m0-broker
  sudo -u "$BROKER" git config --global user.email m0-broker@he-toolstack.local
  sudo -u "$BROKER" git config --global init.defaultBranch main
  echo "Broker public key (register as deploy key with WRITE on the EVIDENCE repo ONLY):"
  sudo -u "$BROKER" cat /home/$BROKER/.ssh/id_ed25519.pub
  echo "Then PROVE push works: sudo -u $BROKER git ls-remote $EVID"
fi
[[ -f /home/$BROKER/.m0-evidence-remote ]] || echo "$EVID" > /home/$BROKER/.m0-evidence-remote
# systemd unit (the thing that makes 'not a daemon' false).
cat > /etc/systemd/system/m0-broker.service <<EOF
[Unit]
Description=M0 interview evidence broker (§3.3)
After=network-online.target docker.service
Wants=network-online.target

[Service]
User=$BROKER
Group=$BROKER
ExecStart=/usr/bin/python3 /opt/m0-broker/runner.py --daemon
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/opt/m0-broker
EOF
systemctl daemon-reload
systemctl enable --now m0-broker   # script starts it; active is a cutover gate
echo
echo "Phase 1 complete. Owner's remaining manual acts (honest count):"
echo "  1. register broker deploy key on evidence repo (above); PROVE write"
echo "  2. enable branch protection on the evidence repo (append-only path rule)"
echo "  3. verify service: systemctl status m0-broker && sudo -u $BROKER /opt/m0-broker/runner.py --verify"
echo "  4. run phase 2: sudo $0 $REPO --confirm-cutover"
echo "     (lists all credentials; re-run with M0_CUTOVER_CONFIRMED=yes to execute)"
echo "  5. prove revocation from the container + run §3.6 tests (a)-(d)"
echo "Total: 3 script invocations (phase 1; phase 2 inventory; phase 2 confirm) + the"
echo "manual acts listed in the protocol §8."
