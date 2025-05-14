import time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from .utils import normalize_url

RETRY_COUNT = 3
RETRY_DELAY = 10  # seconds

def fetch_and_parse(url):
    # Fetch the URL (with retries) and parse into hierarchical dict.
    last_exc = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text
            break
        except Exception as e:
            last_exc = e
            print(f"[Attempt {attempt}] Error Fetching {url}: {e}")  # TODO Log it '#error-handling'
            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY)
    else:
        raise last_exc

    soup = BeautifulSoup(html, "html.parser")

    # Extract the <h1> that contains "week" (if any), else first <h1>
    h1 = None
    for tag in soup.find_all("h1"):
        if "week" in tag.get_text(strip=True).lower():
            h1 = tag
            break
    if not h1:
        h1 = soup.find("h1")
    if not h1:
        raise RuntimeError("No <h1> found on page to extract title")  # TODO Log it '#error-handling'

    # e.g. <a href="#week-0-functions"><em>Functions</em></a>
    anchor = None
    for a in h1.find_all("a", href=True):
        if a["href"].startswith("#week"):
            anchor = a
            break
    raw = anchor["href"].lstrip("#") if anchor else h1.get_text().strip()
    title = raw.replace(" ", "-").lower()

    # Build Hierarchy from the first top-level list (<ul> or <ol>) after <h1>
    container = None
    for sib in h1.next_siblings:
        if getattr(sib, "name", None) in ("ul", "ol"):
            container = sib
            break

    structure = {"title": title}
    if container:
        structure["content"] = _parse_list(container, url)
    else:
        structure["content"] = {}

    return structure


def _parse_list(node, base_url):
    # Recursively parse a <ul> or <ol> into a list of dicts:
    # [{"label": "...", "url": "...", "children": [...]}, ...]
    items = []

    for li in node.find_all("li", recursive=False):
        entry = {}

        # Label: first direct text or non-list child text
        label = ""
        for child in li.contents:
            if child.name in ("ul", "ol"):
                continue
            text = child.get_text(strip=True) if hasattr(child, 'get_text') else child.strip()
            if text:
                label = text
                break
        entry["label"] = label

        # Children: nested lists
        child_list = li.find(["ul", "ol"], recursive=False)
        if child_list:
            entry["children"] = _parse_list(child_list, base_url)
        else:
            # URL: only if no nested list
            link = li.find("a", href=True, recursive=False)
            if link:
                href = urljoin(base_url, link["href"])
                entry["url"] = normalize_url(href)

        items.append(entry)
    return items

# Signature: requests.get(url, params=None, **kwargs) -> Response
# Docs: https://docs.python-requests.org/en/master/api/#requests.get
# Signature: urljoin(base: str, url: str) -> str
# Docs: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin
# Signature: find(name=None, attrs={}, recursive=True, text=None, **kwargs)
# Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find
# Signature: Response.raise_for_status() -> None
# Docs: https://docs.python-requests.org/en/master/api/#requests.Response.raise_for_status
# Signature: BeautifulSoup(markup, parser) -> BeautifulSoup
# Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#beautifulsoup
# Docs: https://docs.python.org/3/library/time.html#time.sleep
