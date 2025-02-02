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
OUTPUT_FILE = Path(__file__).parent / "status.html"

def default_check(url: str) -> tuple[str, str]:
    response = urllib.request.urlopen(url)
    if response.code != HTTPStatus.OK:
        return ICON_ERROR, MSG_ERROR
    return ICON_OK, MSG_OK


if __name__ == "__main__":
    template_page = Template(TEMPLATE_FILE.read_text())

    checks = {
        ("WEBSITE", "https://www.openml.org/"): default_check,
        ("MINIO", "https://data.openml.org/minio/health/live"): default_check,
        ("REST", "https://www.openml.org/api/v1/json/evaluationmeasure/list"): default_check,
        ("TEST", "https://test.openml.org/"): default_check,
        ("ES", "https://es.openml.org/"): default_check,
    }

    statuses = {}
    for (name, url), check in checks.items():
        icon, msg = check(url)
        statuses.update({f"{name}_STATUS": msg, f"{name}_STATUS_ICON": icon})


    OUTPUT_FILE.write_text(
        template_page.substitute(**statuses)
    )


