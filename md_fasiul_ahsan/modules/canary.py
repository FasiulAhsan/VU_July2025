# # md_fasiul_ahsan/modules/canary.py
# import os
# import time
# import json
# import urllib.request
# import boto3

# CW = boto3.client("cloudwatch")

# URL = os.environ["TARGET_URL"]                 # e.g., https://medilinks.com.au/
# NAMESPACE = os.environ.get("NAMESPACE", "Canary")
# SITE = os.environ.get("SITE_NAME", "MainSite")
# TIMEOUT = float(os.environ.get("TIMEOUT_SECONDS", "10"))

# def _put(metric: str, value: float, unit: str | None = None):
#     """Publish a single custom metric with an optional unit."""
#     datum = {
#         "MetricName": metric,
#         "Value": float(value),
#         "Dimensions": [{"Name": "SiteName", "Value": SITE}],  # dimension per site
#     }
#     if unit:
#         datum["Unit"] = unit
#     CW.put_metric_data(Namespace=NAMESPACE, MetricData=[datum])

# def handler(event, context):
#     start = time.perf_counter()
#     ok = 0
#     status = None
#     reason = "ok"

#     try:
#         # User-Agent avoids occasional 403s from some sites/CDNs
#         req = urllib.request.Request(URL, headers={"User-Agent": "Canary/1.0"})
#         with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
#             status = r.status
#             ok = 1 if 200 <= status < 300 else 0     # treat only 2xx as success
#     except Exception as e:
#         reason = f"{type(e).__name__}"

#     latency_ms = (time.perf_counter() - start) * 1000.0

#     # Publish metrics
#     _put("LatencyMs", latency_ms, unit="Milliseconds")
#     _put("Availability", ok)  # unitless Count is fine

#     # Structured log for easy debugging
#     print(json.dumps({
#         "site": SITE,
#         "url": URL,
#         "ok": ok,
#         "status": status,
#         "latency_ms": round(latency_ms, 1),
#         "reason": reason,
#     }))

#     return {"ok": ok, "latency_ms": round(latency_ms, 1), "status": status}



import os, time, json, urllib.request, boto3

cw = boto3.client("cloudwatch")

NAMESPACE = os.environ.get("NAMESPACE", "Canary")
TIMEOUT = float(os.environ.get("TIMEOUT_SECONDS", "10"))

def load_sites():
    """Read modules/sites.json; fall back to env TARGET_URL/SITE_NAME if json missing."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, "sites.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return [s for s in data if "name" in s and "url" in s]
    except Exception:
        url = os.environ.get("TARGET_URL")
        name = os.environ.get("SITE_NAME", "MainSite")
        return [{"name": name, "url": url}] if url else []

def probe(url: str):
    start = time.perf_counter()
    ok, status, reason = 0, None, "ok"
    try:
        # Friendly UA avoids 403s from some CDNs
        req = urllib.request.Request(url, headers={"User-Agent": "Canary/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            status = r.status
            ok = 1 if 200 <= status < 300 else 0
    except Exception as e:
        reason = type(e).__name__
    latency_ms = (time.perf_counter() - start) * 1000.0
    return ok, latency_ms, status, reason

def handler(event, context):
    """Run once per schedule; publish Availability + LatencyMs per SiteName."""
    results = []
    sites = load_sites()
    print("loaded_sites:", [s["name"] for s in sites])

    for s in sites:
        name, url = s["name"], s["url"]
        ok, lat_ms, status, reason = probe(url)

        # send both metrics in one call (efficient)
        cw.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[
                {
                    "MetricName": "Availability",
                    "Value": float(ok),
                    "Dimensions": [{"Name": "SiteName", "Value": name}],
                },
                {
                    "MetricName": "LatencyMs",
                    "Value": float(lat_ms),
                    "Unit": "Milliseconds",
                    "Dimensions": [{"Name": "SiteName", "Value": name}],
                },
            ],
        )

        print(json.dumps({
            "site": name, "url": url, "ok": ok,
            "status": status, "latency_ms": round(lat_ms, 1),
            "reason": reason
        }))
        results.append({"site": name, "ok": ok, "latency_ms": round(lat_ms, 1)})

    return {"results": results}
