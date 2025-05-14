import os
from pathlib import Path

def write_ip_if_changed(ip: str) -> bool:
    path = Path(os.getenv("LAST_IP_FILE"))
    old = path.read_text().strip() if path.exists() else None
    if ip != old:
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(ip + "\n")
        return True
    return False