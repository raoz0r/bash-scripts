import os
import time
from dotenv import load_dotenv
from services.ai_checker import process_files
from services.markdown_parser import extract_frontmatter
from services.markdown_to_json import extract_markdown_structure, save_markdown_json
from utils.logger import log_processing_result, log_error, logger
import json

load_dotenv()
NOTES_FOLDER = os.getenv("NOTES_FOLDER")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")

class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def save_combined_json(frontmatter, structure, file_path, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        json_path = os.path.join(output_dir, f"{file_name}.json")
        
        combined = {
            "frontmatter": frontmatter,
            "structure": structure
        }

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(combined, json_file, indent=2, ensure_ascii=False, cls=SafeEncoder)
            
        logger.info(f"Saved combined JSON to {json_path}", extra={"status": "saved_combined_json"})
        return json_path
        
    except Exception as e:
        logger.error(f"Error saving combined JSON to {json_path}", extra={
            "status": "error_saving_combined_json",
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        return None

def main():
    logger.info("💥 Application starting", extra={"status": "startup"})

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

        for md in ai_files:
            logger.info(f"Processing file {md}", extra={"status": "processing_file"})

            # Extract frontmatter
            fm = extract_frontmatter(md)
            if not fm:
                logger.warning(f"No frontmatter extracted from {md}", extra={"status": "missing_frontmatter"})
                continue

            # Extract full markdown structure
            structure = extract_markdown_structure(md)
            if not structure:
                logger.warning(f"No structure extracted from {md}", extra={"status": "missing_structure"})
                continue

            # Save combined JSON
            if save_combined_json(fm, structure, md, OUTPUT_FOLDER):
                saved += 1
                logger.info(f"Combined JSON saved for {md}", extra={"status": "combined_saved"})

        log_processing_result(
            status="indexed_combined",
            duration_sec=round(time.time() - start_fm, 2),
            files_indexed=saved
        )

        print(f"\n ✅ Processed {saved} files with combined JSON in {OUTPUT_FOLDER}")
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
