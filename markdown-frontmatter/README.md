
# DevOps Daily Journal (Archived)

> ⚠️ This project is no longer actively maintained. Although the core functionality remains operational, it has been deprecated in favor of a more integrated and sustainable solution using native Obsidian plugins.

## Project Summary

**DevOps Daily Journal** was developed as a lightweight, script-driven logging system aimed at engineers, developers, and creators who prefer Markdown-based workflows. It offered a CLI-friendly way to generate structured daily logs and manage metadata tags automatically — all while staying compatible with [Obsidian](https://obsidian.md/), a Markdown knowledge base tool.

This documentation outlines its core features, functionality, and how it supports observability within personal knowledge systems.

## Features

* 📝 Generate pre-formatted daily log templates
* 🧠 Auto-inject metadata tags into Obsidian-compatible YAML front matter
* 🛡 Track tag updates over time to monitor content drift
* 🧰 Fully CLI-compatible — suitable for automation with cron

---

## System Behavior

### Log Format

Each operation logs a structured message to `taglog.log`:

```
level=<log_level> event=<event_name> file=<file_name> [reason=<reason>] [tags=<tags>]
```

**Examples:**

```
level=warn event=tag_skipped file=example.md reason=malformed_front_matter
level=info event=tag_injected file=example.md tags=devops,grafana,loki,promtail
```

---

## Folder Structure

```
devops-daily-journal/
├── README.md
├── LICENSE
├── scripts/
│   ├── newlog.py          # creates daily log entries
│   └── taglog.py          # manages and tracks metadata tags
├── bin/
│   ├── newlog             # optional symlink to newlog.py
│   └── taglog             # optional symlink to taglog.py
├── logs/
│   └── taglog.log         # default log output
├── tests/
│   └── test_taglog.py     # test placeholder
├── requirements.txt
└── .gitignore
```

---

## `taglog.py`: Tag Management

### Purpose

Automates metadata tag injection and drift tracking for Markdown notes using Obsidian’s front matter system.

### Key Features

1. **File Detection**: Scans for `.md` files modified in the past 24 hours
2. **Tag Injection**: Parses inline hashtags (from line 3), adds them to YAML front matter if missing
3. **Structured Logging**: Logs every action to `taglog.log` using a clear and consistent format
4. **CLI Integration**: Ideal for cronjobs, pipelines, or automation environments

### Example Workflow

Given a Markdown file without front matter:

```markdown
# 19.04.2025  
#docker #grafana #promtail
```

The script will transform it into:

```markdown
---
tags:
  - docker
  - grafana
  - promtail
---

# 19.04.2025  
#docker #grafana #promtail
```

And log the event:

```
2025-04-19T13:00:00 level=info event=tag_injected file=19-04-2025.md tags=docker,grafana,promtail
```

---

## Notes & Limitations

* Uses `PyYAML` for YAML parsing
* Will not overwrite valid tag metadata
* Rejects files with:

  * No hashtags
  * Invalid YAML
  * Read/write errors
* Errors are logged silently; there is no terminal output by default
* Designed for personal usage, not enterprise-level systems

---

## Rationale

This tool was created out of frustration with the lack of structured metadata management in traditional journaling workflows. Rather than keeping disorganized notes, the author envisioned a system that allowed visibility into the "state" of thought and logs — similar to observability in distributed systems.

> “He didn’t want a journal. He wanted observability for his soul.”

That vision has since been surpassed by native plugin solutions in Obsidian, making this script a valuable but now archived utility.

---

## License

This project is open for educational and personal use. No specific license applies.

---
Generated by Agent TL;DR v0.0.1  
:: Documentation unit booted under Project ARGUS  
:: Status: markdown_verbosity module = ONLINE  
"Summarizes everything. Writes too much."
