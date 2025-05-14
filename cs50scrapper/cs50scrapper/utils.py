import os
import json
from urllib.parse import urlparse, urlunparse

def normalize_url (raw_url):
    # Example:
    # Input:  "https://example.com/page?utm=stuff#section1"
    # Output: "https://example.com/page"
    # Parse a URL into 6 components:<scheme>://<netloc>/<path>;<params>?<query>#<fragment>

    p = urlparse(raw_url)
    clean = p._replace(query="", fragment="")
    return urlunparse(clean)

def dump_json (data, folder):
    # Write data to cs50/<folder>/<title>.json, creating dir when necessary.
    # Assume data ditionary always contains a title key, which could lead to errors
    # TODO: Add '#error-handling' for such cases.

    out_dir = os.path.join("cs50", folder)
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{data['title']}.json"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

