import sys
from urllib.parse import urlparse
from .scrapper import fetch_and_parse
from .utils import dump_json

def main():
    if len(sys.argv) != 2:
        print("Usage: cs50scrapper <course_page_url>")
        sys.exit(1)

    url = sys.argv[1]
    data = fetch_and_parse(url)

    # derive folder name = first non-empty segment of the URL path
    # e.g. https://cs50.harvard.edu/python/2022/weeks/0/  →  "python"
    parsed = urlparse(url)
    segments = [seg for seg in parsed.path.split("/") if seg]
    if not segments:
        print("Error: couldn't determine course folder from URL path.") # TODO: Log it #error-handling
        sys.exit(1)
    folder = segments[0]

    dump_json(data, folder)
    print(f"→ JSON written to cs50/{folder}/{data['title']}.json")

if __name__ == "__main__":
    main()
