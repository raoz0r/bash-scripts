import os
import time

def discover_markdown_files(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.md'):
                yield os.path.join(root, file)

def check_line_3_for_ai(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for _ in range(2):  # Skip first two lines
                next(f)
            third_line = next(f).strip().lower()
            return 'ai: yes' in third_line
    except (StopIteration, FileNotFoundError, UnicodeDecodeError):
        return False

def process_files(folder):
    start_time = time.time()

    try:
        all_files = list(discover_markdown_files(folder))
        ai_files = [f for f in all_files if check_line_3_for_ai(f)]
    
        return {
            "destination_path": os.path.abspath(folder),
            "duration_sec": round(time.time() - start_time, 2),
            "files_scanned": len(all_files),
            "files_indexed": len(ai_files),
            "ai_files": ai_files
        }
    except Exception as e:
        raise
