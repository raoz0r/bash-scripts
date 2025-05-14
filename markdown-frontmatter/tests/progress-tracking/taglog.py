#!/usr/bin/env python3

# Log message format:
# level=<log_level> event=<event_name> file=<file_name> [reason=<reason>] [tags=<tags>]
# Example: level=warn event=tag_skipped file=example.md reason=malformed_front_matter

#!/usr/bin/env python3

import os
import sys
import re
import time
import yaml
from datetime import datetime

# Configuration
TARGET_DIR = "/mnt/storage/keys-scripts/devops-daily-journal/tests/progress-tracking" # This is a test directory for the script. In production, this should be set to the actual target directory.
LOG_FILE = "/mnt/storage/logs/taglog-test.log" # This is a test log file for the script. In production, this should be set to the actual log file.
ONE_DAY = 86400  # seconds


def read_latest_info_tags(file_name):
    """
    Read the log file and return the tags from the newest level=info entry for the given file.
    """
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            # Extract key=value pairs
            parts = dict(re.findall(r"(\w+)=([^\s]+)", line))
            if parts.get('level') == 'info' and parts.get('file') == file_name:
                tags = parts.get('tags', '')
                tag_list = tags.split(',') if tags else []
                timestamp = line.split()[0]
                entries.append((timestamp, tag_list))
    if not entries:
        return []
    # Return tags from the latest entry
    entries.sort(key=lambda x: x[0])
    return entries[-1][1]


def parse_frontmatter(lines):
    """
    Detect and parse YAML front matter. Returns (data, start_idx, end_idx) or (None, None, None).
    """
    if not lines or lines[0].strip() != '---':
        return None, None, None
    # find closing '---'
    for idx in range(1, len(lines)):
        if lines[idx].strip() == '---':
            yaml_block = ''.join(lines[1:idx])
            try:
                data = yaml.safe_load(yaml_block) or {}
            except yaml.YAMLError:
                return None, None, None
            return data, 0, idx
    return None, None, None


def build_frontmatter(tags):
    """
    Build a YAML front matter string given a list of tags.
    """
    doc = {'tags': tags}
    yaml_content = yaml.dump(doc, default_flow_style=False, sort_keys=False, indent=2).strip() + '\n'
    return '---\n' + yaml_content + '---\n\n'


def log_event(level, event, file_name, reason=None, tags=None):
    """
    Append a log entry with timestamp, level, event, file, and optional reason or tags.
    Dynamically assigns app=<calling script name>.
    """
    app_name = os.path.basename(sys.argv[0])
    
    components = [
        f"level={level}",
        f"event={event}",
        f"file={file_name}",
        f"app={app_name}"
    ]
    if reason:
        components.append(f"reason={reason}")
    if tags is not None:
        components.append(f"tags={','.join(tags)}")
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} " + " ".join(components)
    with open(LOG_FILE, 'a') as logf:
        logf.write(entry + '\n')



def process_file(path):
    file_name = os.path.basename(path)
    try:
        with open(path) as f:
            lines = f.readlines()
    except Exception:
        log_event('warn', 'tag_skipped', file_name, reason='read_error')
        return

    data, start, end = parse_frontmatter(lines)
    # Case 1: existing YAML
    if data is not None:
        if 'tags' not in data or not isinstance(data['tags'], list):
            log_event('warn', 'tag_skipped', file_name, reason='malformed_front_matter')
            return
        current_tags = data['tags']
        latest_tags = read_latest_info_tags(file_name)
        if set(current_tags) != set(latest_tags):
            log_event('info', 'tag_updated', file_name, tags=current_tags)
        return

    # Case 2: no YAML, look for inline tags on line 3
    if len(lines) < 3:
        log_event('warn', 'tag_skipped', file_name, reason='no_tags_found')
        return
    inline_tags = re.findall(r"#([\w-]+)", lines[2])
    if not inline_tags:
        log_event('warn', 'tag_skipped', file_name, reason='no_tags_found')
        return

    # Inject new front matter
    new_front = build_frontmatter(inline_tags)
    new_content = [new_front] + lines
    try:
        with open(path, 'w') as f:
            f.writelines(new_content)
    except Exception:
        log_event('warn', 'tag_skipped', file_name, reason='write_error')
        return

    log_event('info', 'tag_injected', file_name, tags=inline_tags)

def finalize_daily_log():
    """
    Ensure a single daily_log_finalized entry for today's file.
    """
    today = datetime.now().strftime("%d-%m-%Y")
    filename = f"{today}.md"
    marker = f"event=daily_log_finalized file={filename}"
    exists = False
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            for line in f:
                if marker in line:
                    exists = True
                    break
    if not exists:
        log_event('info', 'daily_log_finalized', filename)

def main():
    now = time.time()
    cutoff = now - ONE_DAY
    for root, _, files in os.walk(TARGET_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            try:
                if os.path.getmtime(fpath) >= cutoff:
                    process_file(fpath)
            except Exception:
                log_event('warn', 'tag_skipped', fname, reason='mtime_error')
    # Finalize daily log entry
    finalize_daily_log()


if __name__ == '__main__':
    main()
