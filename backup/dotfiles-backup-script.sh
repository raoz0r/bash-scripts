#!/bin/bash

# Prevent concurrent backups
LOCK_FILE="/tmp/dotfiles_backup.lock"
exec 200>$LOCK_FILE
flock -n 200 || exit 1

# Setup paths and metadata
BACKUP_DIR="/mnt/cortex/backup"
DATE=$(date +%F)
OUTFILE="dotfiles-backup-$DATE.tar.zst"
LOGFILE="/mnt/cortex/logs/backup-log.jsonl"
DEST="$BACKUP_DIR/$OUTFILE"

START_TIME=$(date +%s)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HOSTNAME=$(hostname)
BACKUP_ID="$DATE-daily"
TRIGGER="cron"

mkdir -p "$BACKUP_DIR" "$(dirname "$LOGFILE")"

# Create archive, exclude noisy dirs
tar --exclude='.cache' \
    --exclude='.config/google-chrome' \
    --exclude='.config/obsidian' \
    --exclude='.config/go' \
    --exclude='.local/state/nvim' \
    --exclude='.local/share/nvim' \
    --exclude='.local/share/Trash' \
    --exclude='.local/share/recently-used.xbel' \
    -I 'zstd -19' -cvf "$DEST" \
    "$HOME/.zshrc" \
    "$HOME/.zprofile" \
    "$HOME/.zshenv" \
    "$HOME/.gitconfig" \
    "$HOME/.XCompose" \
    "$HOME/.ssh" \
    "$HOME/.ssh-agent-setup" \
    "$HOME/.local" \
    "$HOME/.config"

# Upload to GDrive
if rclone copy "$DEST" gdrive:dotfiles-backup/; then
    # Collect metrics
    END_TIME=$(date +%s)
    DURATION_SEC=$(( END_TIME - START_TIME ))
    FILE_COUNT=$(tar -tf "$DEST" | wc -l)
    SIZE_MB=$(du -m "$DEST" | awk '{print $1}')

    # Cleanup local file
    rm -f "$DEST"

    # Debug output
    echo "DEBUG S: timestamp=$TIMESTAMP"
    echo "DEBUG S: duration_sec=$DURATION_SEC"
    echo "DEBUG S: file_count=$FILE_COUNT"
    echo "DEBUG S: size_mb=$SIZE_MB"

    # Log success
    jq -n \
      --arg timestamp "$TIMESTAMP" \
      --arg level "info" \
      --arg hostname "$HOSTNAME" \
      --arg app "backup-service" \
      --arg module "daily-routine" \
      --arg backup_id "$BACKUP_ID" \
      --arg status "success" \
      --arg trigger "$TRIGGER" \
      --arg source_path "$DEST" \
      --arg destination_path "gdrive:dotfiles-backup/" \
      --argjson duration_sec "$DURATION_SEC" \
      --argjson files_backed_up "$FILE_COUNT" \
      --argjson total_size_mb "$SIZE_MB" \
      --arg message "Backup completed successfully" \
      '{
        "timestamp": $timestamp,
        "level": $level,
        "hostname": $hostname,
        "app": $app,
        "module": $module,
        "backup_id": $backup_id,
        "status": $status,
        "trigger": $trigger,
        "source_path": $source_path,
        "destination_path": $destination_path,
        "duration_sec": $duration_sec,
        "files_backed_up": $files_backed_up,
        "total_size_mb": $total_size_mb,
        "message": $message
      }' >> "$LOGFILE"
else
    # Log failure
    END_TIME=$(date +%s)
    DURATION_SEC=$(( END_TIME - START_TIME ))

    jq -n \
      --arg timestamp "$TIMESTAMP" \
      --arg level "error" \
      --arg hostname "$HOSTNAME" \
      --arg app "backup-service" \
      --arg module "daily-routine" \
      --arg backup_id "$BACKUP_ID" \
      --arg status "failed" \
      --arg trigger "$TRIGGER" \
      --arg source_path "$DEST" \
      --arg destination_path "gdrive:dotfiles-backup/" \
      --argjson duration_sec "$DURATION_SEC" \
      --argjson files_backed_up 0 \
      --argjson total_size_mb 0 \
      --arg message "Backup failed to upload to gdrive" \
      '{
        "timestamp": $timestamp,
        "level": $level,
        "hostname": $hostname,
        "app": $app,
        "module": $module,
        "backup_id": $backup_id,
        "status": $status,
        "trigger": $trigger,
        "source_path": $source_path,
        "destination_path": $destination_path,
        "duration_sec": $duration_sec,
        "files_backed_up": $files_backed_up,
        "total_size_mb": $total_size_mb,
        "message": $message
      }' >> "$LOGFILE"
fi
