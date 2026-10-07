#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080/fhir")
TEST_DIR = Path(__file__).resolve().parent / "smoketest"
REPORT_PATH = Path(__file__).resolve().with_name("search-parameter-report.html")

RESOURCE_SCENARIOS = {
    "Organization": [
        ("name", "ACME Health Plan"),
        ("type", "pay"),
        ("active", "true"),
    ],
    "Practitioner": [
        ("identifier", "1245319599"),
        ("name", "Provider"),
        ("active", "true"),
    ],
    "Patient": [
        ("identifier", "CARINBB-PAT-001"),
        ("family", "Doe"),
        ("gender", "female"),
        ("birthdate", "1980-06-15"),
    ],
    "RelatedPerson": [
        ("patient", "Patient/patient-carin-1"),
        ("relationship", "SPS"),
        ("name", "Doe"),
    ],
    "Coverage": [
        ("beneficiary", "Patient/patient-carin-1"),
        ("payor", "Organization/org-carin-1"),
        ("subscriber", "Patient/patient-carin-1"),
        ("status", "active"),
    ],
    "Encounter": [
        ("patient", "Patient/patient-carin-1"),
        ("subject", "Patient/patient-carin-1"),
        ("status", "finished"),
    ],
    "Condition": [
        ("patient", "Patient/patient-carin-1"),
        ("subject", "Patient/patient-carin-1"),
        ("code", "44054006"),
    ],
    "Observation": [
        ("patient", "Patient/patient-carin-1"),
        ("subject", "Patient/patient-carin-1"),
        ("code", "29463-7"),
        ("status", "final"),
    ],
}


def get_json(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/fhir+json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload) if payload else {}


def put_resource(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as handle:
        resource = json.load(handle)
    resource_type = resource.get("resourceType")
    resource_id = resource.get("id")
    if not resource_type or not resource_id:
        raise ValueError(f"Missing resourceType or id in {file_path}")
    url = f"{BASE_URL}/{resource_type}/{resource_id}"
    body = json.dumps(resource).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="PUT",
        headers={"Content-Type": "application/fhir+json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


def ensure_smoke_resources():
    files = [
        TEST_DIR / "01-organization.json",
        TEST_DIR / "02-practitioner.json",
        TEST_DIR / "03-patient.json",
        TEST_DIR / "04-relatedperson.json",
        TEST_DIR / "05-coverage.json",
        TEST_DIR / "06-encounter.json",
        TEST_DIR / "07-condition.json",
        TEST_DIR / "08-observation.json",
    ]
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise FileNotFoundError(f"Required smoke-test files missing: {missing}")
    for file_path in files:
        put_resource(file_path)


def get_supported_search_params():
    metadata = get_json(f"{BASE_URL}/metadata")
    supported = {}
    for entry in metadata.get("rest", [{}])[0].get("resource", []):
        resource_type = entry.get("type")
        names = {param.get("name") for param in entry.get("searchParam", []) if param.get("name")}
        supported[resource_type] = names
    return supported


def run_search_test(resource_type: str, param_name: str, param_value: str):
    encoded_value = urllib.parse.quote(str(param_value), safe="")
    url = f"{BASE_URL}/{resource_type}?{param_name}={encoded_value}"
    try:
        bundle = get_json(url)
    except Exception as exc:
        return {
            "resourceType": resource_type,
            "param": param_name,
            "value": param_value,
            "status": "FAIL",
            "details": f"Request error: {exc}",
        }

    total = int(bundle.get("total", 0) or 0)
    entries = bundle.get("entry", [])
    matched = any(
        (entry.get("resource", {}).get("resourceType") == resource_type)
        for entry in entries
    )
    ok = total > 0 and matched
    return {
        "resourceType": resource_type,
        "param": param_name,
        "value": param_value,
        "status": "PASS" if ok else "FAIL",
        "details": f"total={total}, matched={matched}",
    }


def build_html(results):
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    total = len(results)
    pass_rate = (passed / total * 100) if total else 0
    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8' />",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0' />",
        "  <title>CARIN BB Search Parameter Test Report</title>",
        "  <style>",
        "    body { font-family: Arial, sans-serif; margin: 32px; color: #1f2933; background: #f8fafc; }",
        "    .summary { background: #ffffff; border: 1px solid #dfe3e8; border-radius: 8px; padding: 20px; margin-bottom: 20px; }",
        "    .cards { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }",
        "    .card { background: #fff; border: 1px solid #dfe3e8; border-radius: 8px; padding: 18px 20px; min-width: 150px; }",
        "    .label { font-size: 12px; color: #52606d; text-transform: uppercase; letter-spacing: 0.05em; }",
        "    .value { font-size: 28px; font-weight: bold; margin-top: 8px; }",
        "    table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #dfe3e8; }",
        "    th, td { border-bottom: 1px solid #dfe3e8; padding: 10px 12px; text-align: left; }",
        "    th { background: #eef2f7; }",
        "    .pass { color: #0f9d58; font-weight: bold; }",
        "    .fail { color: #d93025; font-weight: bold; }",
        "    .meta { color: #52606d; font-size: 12px; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>CARIN BB Search Parameter Test Report</h1>",
        "  <div class='summary'>",
        f"    <p><strong>Base URL:</strong> {BASE_URL}</p>",
        f"    <p><strong>Generated:</strong> {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>",
        "  </div>",
        "  <div class='cards'>",
        f"    <div class='card'><div class='label'>Total</div><div class='value'>{total}</div></div>",
        f"    <div class='card'><div class='label'>Passed</div><div class='value'>{passed}</div></div>",
        f"    <div class='card'><div class='label'>Failed</div><div class='value'>{failed}</div></div>",
        f"    <div class='card'><div class='label'>Pass rate</div><div class='value'>{pass_rate:.1f}%</div></div>",
        "  </div>",
        "  <table>",
        "    <thead><tr><th>Resource</th><th>Search Param</th><th>Value</th><th>Status</th><th>Details</th></tr></thead>",
        "    <tbody>",
    ]
    for row in results:
        cls = "pass" if row["status"] == "PASS" else "fail"
        lines.append(
            "    <tr>"
            f"<td>{row['resourceType']}</td>"
            f"<td>{row['param']}</td>"
            f"<td>{row['value']}</td>"
            f"<td class='{cls}'>{row['status']}</td>"
            f"<td>{row['details']}</td>"
            "</tr>"
        )
    lines.extend([
        "    </tbody>",
        "  </table>",
        "</body>",
        "</html>",
    ])
    return "\n".join(lines)


def main():
    ensure_smoke_resources()
    supported = get_supported_search_params()
    results = []
    for resource_type, scenarios in RESOURCE_SCENARIOS.items():
        for param_name, param_value in scenarios:
            if param_name not in supported.get(resource_type, set()):
                results.append({
                    "resourceType": resource_type,
                    "param": param_name,
                    "value": param_value,
                    "status": "FAIL",
                    "details": "Unsupported by server metadata",
                })
                continue
            results.append(run_search_test(resource_type, param_name, param_value))

    html = build_html(results)
    REPORT_PATH.write_text(html, encoding="utf-8")
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    print(f"Search parameter tests: {passed} passed, {failed} failed")
    print(f"HTML report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
