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
            "destination_path": getattr(record, "destination_path", ""),
            "duration_sec": getattr(record, "duration_sec", 0),
            "files_scanned": getattr(record, "files_scanned", 0),
            "files_indexed": getattr(record, "files_indexed", 0),
            "message": record.getMessage()
        }
        return json.dumps(log_data, ensure_ascii=False)

handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def log_processing_result(status, duration_sec, files_scanned, files_indexed, destination_path):
    logger.debug(
        f"Scanned {files_scanned} files, indexed {files_indexed}",
        extra={
            "status": status,
            "duration_sec": duration_sec,
            "files_scanned": files_scanned,
            "files_indexed": files_indexed,
            "destination_path": destination_path
        }
    )

