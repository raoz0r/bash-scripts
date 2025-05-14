from services.ai_checker import process_files
from utils.logger import log_processing_result, log_error, logger

def main():
    # Add diagnostic logs at the beginning
    logger.info("Application starting", extra={"status": "startup"})
    
    folder = "/home/ghost/argus"
    
    try:
        metrics = process_files(folder)
        
        log_processing_result(
            status="success",
            duration_sec=metrics["duration_sec"],
            files_scanned=metrics["files_scanned"],
            files_indexed=metrics["files_indexed"],
            destination_path=metrics["destination_path"]
        )

        print(f"Found {len(metrics['ai_files'])} files with ai: yes")
        for file in metrics["ai_files"]:
            print(file)
            
    except FileNotFoundError as e:
        log_error(f"Folder not found: {folder}", exception=e, destination_path=folder)
    except PermissionError as e:
        log_error(f"Permission denied accessing: {folder}", exception=e, destination_path=folder)
    except Exception as e:
        log_error("Unexpected error during file processing", exception=e, destination_path=folder)
    finally:
        logger.info("Application ending", extra={"status": "shutdown"})
        
        for handler in logger.handlers:
            handler.flush()

if __name__ == "__main__":
    main() 
