import datetime
import json
from http import HTTPStatus
from pathlib import Path
import urllib.request
from string import Template

ICON_OK = "✅"
ICON_WARN = "⚠️"
ICON_ERROR = "❌"

MSG_OK = "Normal"
MSG_WARN = "Limited Availability"
MSG_ERROR = "Unavailable"

TEMPLATE_FILE = Path(__file__).parent / "status_page_template.html"
OUTPUT_FILE = Path(__file__).parent / "build" / "index.html"

def default_check(url: str) -> tuple[str, str]:
    response = urllib.request.urlopen(url)
    if response.code != HTTPStatus.OK:
        return ICON_ERROR, MSG_ERROR
    return ICON_OK, MSG_OK

def frontend_check(url: str) -> tuple[str, str]:
    response = urllib.request.urlopen(url)
    if response.code != HTTPStatus.OK:
        return ICON_ERROR, MSG_ERROR
    if "<title>OpenML</title>" in response.fp.read().decode("utf-8"):
        return ICON_OK, MSG_OK
    return ICON_WARN, "Server reachable, website unavailable."

def elastic_search_check(url: str) -> tuple[str, str]:
    response = urllib.request.urlopen(url)
    if response.code != HTTPStatus.OK:
        return ICON_ERROR, MSG_ERROR
    status = json.load(response)
    match status:
        case {"status": "green"}:
            return ICON_OK, MSG_OK
        case {"status": "yellow", "unassigned_shards": n}:
            return ICON_OK, MSG_OK  # Current Production is permanently yellow. Nothing to worry about.
        case {"status": "red", "unassigned_shards": n}:
            return ICON_ERROR, "Index and search operations may fail."
        case _:
            return ICON_ERROR, "Unknown error while fetching cluster health."


if __name__ == "__main__":
    template_page = Template(TEMPLATE_FILE.read_text())

    checks = {
        ("WEBSITE", "https://www.openml.org/"): frontend_check,
        ("MINIO", "https://data.openml.org/minio/health/live"): default_check,
        ("REST", "https://www.openml.org/api/v1/json/evaluationmeasure/list"): default_check,
        ("TEST", "https://test.openml.org/"): frontend_check,
        ("ES", "https://es.openml.org/_cluster/health?wait_for_status=yellow&timeout=10s&pretty"): elastic_search_check,
    }

    statuses = {}
    for (name, url), check in checks.items():
        icon, msg = check(url)
        statuses.update({f"{name}_STATUS": msg, f"{name}_STATUS_ICON": icon})

    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now.isoformat(sep=" ", timespec="seconds")
    statuses["TIMESTAMP"] = timestamp[:-len("+00:00")]
    OUTPUT_FILE.write_text(
        template_page.substitute(**statuses)
    )
