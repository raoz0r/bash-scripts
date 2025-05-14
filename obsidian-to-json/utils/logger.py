import logging
import json
import socket
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
os.makedirs("output", exist_ok=True)

# Static configuration
HOSTNAME = socket.gethostname()
APP_NAME = "obsidian-to-json"
TRIGGER = os.getenv("TRIGGER", "manual")
ENV = os.getenv("ENV", "dev")
EXECUTION_ID = str(uuid.uuid4())

# Configure logger
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("output/obsidian-to-json.log")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname.lower(),
            "hostname": HOSTNAME,
            "app": APP_NAME,
            "execution_id": EXECUTION_ID,
            "status": getattr(record, "status", "unknown"),
            "trigger": TRIGGER,
            "env": ENV,
            "message": record.getMessage()
        }

        # Only include optional fields if they were provided and are meaningful
        optional_fields = ["destination_path", "duration_sec", "files_scanned", "files_indexed"]
        for field in optional_fields:
            if hasattr(record, field):
                value = getattr(record, field)
                if value not in (None, "", 0):
                    log_data[field] = value

        return json.dumps(log_data, ensure_ascii=False)

handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def log_processing_result(status, **additional_info):
    extra_info = {"status": status}

    for key in ["duration_sec", "files_scanned", "files_indexed", "destination_path"]:
        value = additional_info.get(key)
        if value not in (None, "", 0):
            extra_info[key] = value

    logger.info("Processing result", extra=extra_info)

def log_error(error_message, exception=None, **additional_info):
    extra_info = {"status": "error"}

    # Only include extras if they actually make sense
    for key in ["destination_path", "duration_sec", "files_scanned", "files_indexed"]:
        value = additional_info.get(key)
        if value not in (None, "", 0):
            extra_info[key] = value

    if exception:
        extra_info["error_type"] = type(exception).__name__
        extra_info["error_details"] = str(exception)

    # Allow other random extra stuff
    for key, value in additional_info.items():
        if key not in extra_info:
            extra_info[key] = value

    logger.error(error_message, extra=extra_info)
