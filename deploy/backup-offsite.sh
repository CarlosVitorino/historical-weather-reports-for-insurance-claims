#!/usr/bin/env bash
# Copy Weather Evidence's data off this host. Run nightly from root's cron, after the app's own daily copy:
#   30 3 * * *  BACKUP_REMOTE=u123456@u123456.your-storagebox.de:weatherevidence \
#               /opt/weatherevidence/deploy/backup-offsite.sh >> /var/log/weatherevidence-backup.log 2>&1
#
# What goes: backups/ (one consistent database copy per day, BACKUP_KEEP kept) and orders/ (each order's PDF and
# the source snapshots it was built from, so any report can be regenerated and verified). The live app.db is
# skipped: a copy taken mid-write can be torn, and backups/ holds a consistent one taken a moment earlier.
#
# Append-only on purpose: no --delete, so an order removed here by mistake still exists there. Housekeeping only
# deletes unpaid drafts, so the remote grows by roughly the size of the paid orders (~12 MB each, mostly map tiles).
#
# The remote is any rsync-over-ssh target. A Hetzner Storage Box needs `-e "ssh -p 23"`: set BACKUP_SSH_PORT=23.
# Restore: stop the app, copy orders/ back into the volume, gunzip the newest backups/app-*.db.gz to app.db.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
remote="${BACKUP_REMOTE:?set BACKUP_REMOTE to user@host:path}"
port="${BACKUP_SSH_PORT:-22}"
volume="${BACKUP_VOLUME:-weatherevidence_data}"

# A fresh consistent copy first, so the remote is at most minutes behind rather than up to a day.
docker compose -f "$here/compose.yml" exec -T web python -m wxreport.cli backup >/dev/null

src="$(docker volume inspect -f '{{.Mountpoint}}' "$volume")"
rsync -a --partial --exclude 'app.db' --exclude 'app.db-*' -e "ssh -p $port -o BatchMode=yes" "$src/" "$remote/"
echo "$(date -u +%FT%TZ) copied $(du -sh "$src" | cut -f1) to $remote"
