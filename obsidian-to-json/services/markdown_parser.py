import re
import json
import os
import time
from utils.logger import logger
import yaml

def extract_frontmatter(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract the part between ---
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.search(frontmatter_pattern, content, re.DOTALL)
        
        if not match:
            logger.warning(f"No frontmatter found in {file_path}", extra={"status": "no_frontmatter"})
            return {}
        
        frontmatter_text = match.group(1)

        # Use yaml.safe_load for actual parsing
        frontmatter_dict = yaml.safe_load(frontmatter_text)
        
        if not isinstance(frontmatter_dict, dict):
            logger.warning(f"Frontmatter is not a valid YAML dictionary in {file_path}", extra={"status": "invalid_frontmatter"})
            return {}

        return frontmatter_dict

    except Exception as e:
        logger.error(f"Error extracting frontmatter from {file_path}", extra={
            "status": "error_frontmatter",
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        return {}
class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def save_frontmatter_to_json(frontmatter, file_path, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        json_path = os.path.join(output_dir, f"{file_name}.json")
        
        # Save frontmatter as JSON
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(frontmatter, json_file, indent=2, ensure_ascii=False, cls=SafeEncoder)
            
        logger.info(f"Saved frontmatter to {json_path}", extra={"status": "saved_frontmatter"})
        return json_path
        
    except Exception as e:
        logger.error(f"Error saving frontmatter to JSON for {file_path}", extra={
            "status": "error_saving_frontmatter",
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        return None


