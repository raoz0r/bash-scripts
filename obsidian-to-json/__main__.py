from services.ai_checker import process_files
from utils.logger import log_processing_result

def main():
    folder = "/home/ghost/argus"
    metrics = process_files(folder)
    
    log_processing_result(
        status="success",
        duration_sec=metrics["duration_sec"],
        files_scanned=metrics["files_scanned"],
        files_indexed=metrics["files_indexed"],
        destination_path=metrics["destination_path"]
    )

    print(f"Found {len(metrics['ai_files'])} files with ai: yes")  # Fixed missing parenthesis
    for file in metrics["ai_files"]:
        print(file)

if __name__ == "__main__":
    main()
