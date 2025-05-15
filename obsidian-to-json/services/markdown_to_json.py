import re
import json
import os
from utils.logger import logger
import jsonschema

class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def extract_markdown_structure(file_path):
    try:
        logger.info(f"Processing markdown file {file_path}", extra={"status": "start_processing"})
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter
        content = re.sub(r'^---.*?---\s*\n', '', content, flags=re.DOTALL)

        result = {}
        current_section = None
        current_subsection = None
        capture_mode = None
        buffer = []
        in_code_block = False
        code_language = None

        lines = content.splitlines()

        for line in lines:
            stripped = line.strip()

            # Handle code blocks
            if stripped.startswith('```'):
                if not in_code_block:
                    if len(stripped) > 3:
                        code_language = stripped[3:]
                    in_code_block = True
                    if buffer:
                        _flush_buffer(result[current_section]["sections"][current_subsection] if current_subsection 
                                   else result[current_section], capture_mode, buffer, current_section, current_subsection)
                    buffer = []
                    capture_mode = "code"
                    continue
                else:
                    in_code_block = False
                    if buffer:
                        target = result[current_section]["sections"][current_subsection] if current_subsection else result[current_section]
                        if "code_blocks" not in target:
                            target["code_blocks"] = []
                        target["code_blocks"].append({
                            "language": code_language,
                            "content": '\n'.join(buffer)
                        })
                    buffer = []
                    code_language = None
                    capture_mode = None
                    continue

            if in_code_block:
                buffer.append(line)
                continue

            # Handle main sections and subsections
            if stripped.startswith('# '):
                if current_section and buffer:
                    _flush_buffer(result[current_section], capture_mode, buffer, current_section, None)

                current_section = stripped[2:].strip()
                result[current_section] = {"description": "", "sections": {}}
                current_subsection = None
                capture_mode = None
                buffer = []
                logger.info(f"New main section: {current_section}", extra={"status": "new_section"})

            elif stripped.startswith('## '):
                if current_subsection and buffer:
                    _flush_buffer(result[current_section]["sections"][current_subsection], capture_mode, buffer, current_section, current_subsection)
                current_subsection = stripped[3:].strip()
                result[current_section]["sections"][current_subsection] = {}
                capture_mode = None
                buffer = []
                logger.info(f"New subsection: {current_subsection}", extra={"status": "new_subsection"})

            # Handle special flags
            elif stripped.startswith('**') and stripped.endswith('**'):
                if buffer:
                    target = result[current_section]["sections"][current_subsection] if current_subsection else result[current_section]
                    _flush_buffer(target, capture_mode, buffer, current_section, current_subsection)
                
                flag_type = stripped.strip('*').lower()
                if flag_type in ['flags', 'commands', 'code', 'description', 'bullets', 'links']:
                    capture_mode = flag_type
                    buffer = []
                    logger.info(f"Switching capture mode to {capture_mode}", extra={"status": "capture_mode"})

            elif stripped:
                buffer.append(line)

        # Flush any remaining buffer
        if buffer:
            target = result[current_section]["sections"][current_subsection] if current_subsection else result[current_section]
            _flush_buffer(target, capture_mode, buffer, current_section, current_subsection)

        logger.info(f"Finished processing markdown file {file_path}", extra={"status": "finished_processing"})
        return result

    except Exception as e:
        logger.error(f"Error parsing markdown file: {file_path}", extra={
            "status": "error_processing",
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        return None

def _flush_buffer(target, mode, buffer, section_name=None, subsection_name=None):
    text = '\n'.join(buffer).strip()
    if not text:
        return

    if (section_name and section_name.lower() == "resources") or (subsection_name and subsection_name.lower() == "resources"):
        target["links"] = _parse_links(text)
        logger.info(f"Auto-detected 'Resources' section or subsection, parsed {len(target['links'])} links", 
                   extra={"status": "parsed_links"})
        return

    if mode == "description":
        target["description"] = text
    elif mode == "bullets":
        target["bullets"] = _parse_bullets(text)
        logger.info(f"Parsed bullets block with {len(target['bullets'])} bullets", 
                   extra={"status": "parsed_bullets"})
    elif mode == "links":
        target["links"] = _parse_links(text)
        logger.info(f"Parsed links block with {len(target['links'])} links", 
                   extra={"status": "parsed_links"})
    elif mode == "flags":
        target["flags"] = _parse_flags(text)
        logger.info(f"Parsed flags block with {len(target['flags'])} flags", 
                   extra={"status": "parsed_flags"})
    elif mode == "commands":
        target["commands"] = _parse_commands(text)
        logger.info(f"Parsed commands block with {len(target['commands'])} commands", 
                   extra={"status": "parsed_commands"})
    else:
        if "description" in target and target["description"]:
            target["description"] += "\n" + text
        else:
            target["description"] = text

def _parse_flags(text):
    flags = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('- '):
            flag = stripped[2:].strip()
            if ':' in flag:
                key, value = flag.split(':', 1)
                flags.append({"name": key.strip(), "value": value.strip()})
            else:
                flags.append({"name": flag, "value": True})
    return flags

def _parse_commands(text):
    commands = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('- '):
            command = stripped[2:].strip()
            if ':' in command:
                name, description = command.split(':', 1)
                commands.append({"name": name.strip(), "description": description.strip()})
            else:
                commands.append({"name": command, "description": ""})
    return commands

def _parse_bullets(text):
    bullets = []
    pattern = r'-\s+`([^`]+)`:\s*(.*)'

    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
            
        match = re.match(pattern, stripped)
        if match:
            bullets.append({"label": match.group(1), "description": match.group(2)})
        elif stripped.startswith('- '):
            description = stripped[2:].strip()
            bullets.append({"label": "", "description": description})
    return bullets

def _parse_links(text):
    links = []
    pattern = r'-\s+\[([^\]]+)\]\(([^)]+)\)'

    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
            
        match = re.match(pattern, stripped)
        if match:
            links.append({"text": match.group(1), "url": match.group(2)})
    return links

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

def get_json_schema():
    return {
        "type": "object",
        "properties": {
            "frontmatter": {"type": "object"},
            "structure": {"type": "object"}
        },
        "required": ["frontmatter", "structure"]
    }

def validate_json(data):
    schema = get_json_schema()
    jsonschema.validate(instance=data, schema=schema)

def file_exists_for(md, output_dir):
    base_name = os.path.basename(md)
    file_name = os.path.splitext(base_name)[0]
    json_path = os.path.join(output_dir, f"{file_name}.json")
    return os.path.exists(json_path), json_path

def save_combined_json(frontmatter, structure, file_path, output_dir, dry_run=False, pretty=False):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]
    json_path = os.path.join(output_dir, f"{file_name}.json")
    combined = {
        "frontmatter": frontmatter,
        "structure": structure
    }
    try:
        validate_json(combined)
    except jsonschema.ValidationError as ve:
        logger.error(f"Validation failed for {file_path}", extra={"status": "validation_failed", "file_name": file_path, "error_details": str(ve)})
        return None
    if not dry_run:
        with open(json_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(combined, f, ensure_ascii=False, cls=SafeEncoder, indent=2)
            else:
                json.dump(combined, f, ensure_ascii=False, cls=SafeEncoder, separators=(',', ':'))
    return json_path
