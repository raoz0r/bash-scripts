import re
import json
import os
from utils.logger import logger

def extract_markdown_structure(file_path):
    try:
        logger.info(f"Processing markdown file {file_path}", extra={"status": "start_processing"})
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter if exists
        content = re.sub(r'^---.*?---\s*\n', '', content, flags=re.DOTALL)

        result = {}
        current_section = None
        current_subsection = None
        capture_mode = None
        buffer = []

        lines = content.splitlines()

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('# '):
                if current_section and buffer:
                    _flush_buffer(result[current_section], capture_mode, buffer)

                current_section = stripped[2:].strip()
                result[current_section] = {"description": "", "sections": {}}
                current_subsection = None
                capture_mode = None
                buffer = []
                logger.info(f"New main section: {current_section}", extra={"status": "new_section"})

            elif stripped.startswith('## '):
                if current_subsection and buffer:
                    _flush_buffer(result[current_section]["sections"][current_subsection], capture_mode, buffer)
                current_subsection = stripped[3:].strip()
                result[current_section]["sections"][current_subsection] = {}
                capture_mode = None
                buffer = []
                logger.info(f"New subsection: {current_subsection}", extra={"status": "new_subsection"})

            elif stripped.startswith('**') and stripped.endswith('**'):
                if buffer:
                    target = result[current_section]["sections"][current_subsection] if current_subsection else result[current_section]
                    _flush_buffer(target, capture_mode, buffer)
                capture_mode = stripped.strip('*').lower()
                buffer = []
                logger.info(f"Switching capture mode to {capture_mode}", extra={"status": "capture_mode"})

            elif stripped:
                buffer.append(line)

        if buffer:
            target = result[current_section]["sections"][current_subsection] if current_subsection else result[current_section]
            _flush_buffer(target, capture_mode, buffer)

        logger.info(f"Finished processing markdown file {file_path}", extra={"status": "finished_processing"})
        return result

    except Exception as e:
        logger.error(f"Error parsing markdown file: {file_path}", extra={
            "status": "error_processing",
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        return None

def _flush_buffer(target, mode, buffer):
    text = '\n'.join(buffer).strip()
    if not text:
        return

    if mode == "description":
        target["description"] = text
    elif mode == "bullets":
        bullets = re.findall(r'-\s+(.*)', text)
        target["bullets"] = bullets if bullets else [text]
    else:
        if "description" in target and target["description"]:
            target["description"] += "\n" + text
        else:
            target["description"] = text

def save_markdown_json(data, output_file):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved structured JSON to {output_file}", extra={"status": "saved_json"})
        return output_file
    except Exception as e:
        logger.error(f"Error saving JSON to {output_file}", extra={
            "status": "error_saving_json",
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        return None
