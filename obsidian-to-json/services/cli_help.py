HELP_TEXT = """
Obsidian-to-JSON CLI
====================

Usage:
  python -m obsidian-to-json [OPTIONS]

Options:
  --dry-run           Simulate the process. No files will be written or overwritten.
  --o, --overwrite    Overwrite existing output JSON files.
  --e ENV             Set the environment (prod, int, dev). Default: dev
  --t TRIGGER         Set the trigger (manual, cron, auto). Default: manual
  --help              Show this help message and exit.

Examples:
  # Basic usage (process all new files, skip existing outputs)
  python -m obsidian-to-json

  # Overwrite all output files
  python -m obsidian-to-json --o

  # Dry run (simulate, no changes)
  python -m obsidian-to-json --dry-run

  # Set environment and trigger
  python -m obsidian-to-json --e prod --t cron

Description:
  This tool scans your Obsidian markdown folder, extracts frontmatter and structure, and saves them as JSON files.
  By default, it skips files that already have a corresponding JSON output. Use --o to force overwrite.
  Use --dry-run to see what would happen without making any changes.
  The --e and --t flags are used for logging and observability.
"""

def print_help():
    print(HELP_TEXT) 