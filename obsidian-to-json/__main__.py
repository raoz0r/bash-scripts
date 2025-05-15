import os
import time
from dotenv import load_dotenv
from services.ai_checker import process_files
from services.markdown_parser import extract_frontmatter
from services.markdown_to_json import extract_markdown_structure, save_combined_json, file_exists_for
from utils.logger import log_processing_result, log_error, logger, log_file_result
import argparse
from services.cli_help import print_help
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

NOTES_FOLDER = os.getenv("NOTES_FOLDER")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")

def set_env_vars(env, trigger):
    os.environ["ENV"] = env
    os.environ["TRIGGER"] = trigger

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--dry-run', action='store_true', help='Simulate the process. No files will be written or overwritten.')
    parser.add_argument('--o', '--overwrite', dest='overwrite', action='store_true', help='Overwrite existing output JSON files.')
    parser.add_argument('--e', type=str, default='dev', choices=['prod', 'int', 'dev'], help='Set the environment (prod, int, dev).')
    parser.add_argument('--t', type=str, default='manual', choices=['manual', 'cron', 'auto'], help='Set the trigger (manual, cron, auto).')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output (default is compact).')
    parser.add_argument('--help', action='store_true', help='Show this help message and exit.')
    args = parser.parse_args()

    if args.help:
        print_help()
        return

    set_env_vars(args.e, args.t)
    logger.info("💥 Application starting", extra={"status": "startup", "env": args.e, "trigger": args.t})

    try:
        metrics = process_files(NOTES_FOLDER)
        ai_files = metrics["ai_files"]
        log_processing_result(
            status="scan_complete",
            duration_sec=metrics["duration_sec"],
            files_scanned=metrics["files_scanned"],
            files_indexed=metrics["files_indexed"],
            destination_path=NOTES_FOLDER
        )
        start_fm = time.time()
        saved = 0
        skipped = 0
        def process_file(md):
            exists, json_path = file_exists_for(md, OUTPUT_FOLDER)
            if exists and not args.overwrite:
                log_file_result(md, "already_exists")
                return False
            fm = extract_frontmatter(md)
            if not fm:
                return False
            structure = extract_markdown_structure(md)
            if not structure:
                return False
            if save_combined_json(fm, structure, md, OUTPUT_FOLDER, dry_run=args.dry_run, pretty=args.pretty):
                log_file_result(md, "converted")
                return True
            return False
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_file, md): md for md in ai_files}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    saved += 1
                else:
                    skipped += 1
        log_processing_result(
            status="indexed_combined",
            duration_sec=round(time.time() - start_fm, 2),
            files_indexed=saved
        )
        print(f"\n ✅ Processed {saved} files with combined JSON in {OUTPUT_FOLDER}")
        if skipped:
            print(f" ⏩ Skipped {skipped} files (already exist, error, or missing data)")
        for file in ai_files:
            print(f"- {file}")
    except FileNotFoundError as e:
        log_error(f"Folder not found: {NOTES_FOLDER}", exception=e, destination_path=NOTES_FOLDER)
    except PermissionError as e:
        log_error(f"Permission denied accessing: {OUTPUT_FOLDER}", exception=e, destination_path=OUTPUT_FOLDER)
    except Exception as e:
        log_error("Unexpected error during file processing", exception=e, destination_path=OUTPUT_FOLDER)
    finally:
        logger.info("💀 Application ending. All logs flushed. Goblin out.", extra={"status": "shutdown"})
        for handler in logger.handlers:
            handler.flush()

if __name__ == "__main__":
    main()
