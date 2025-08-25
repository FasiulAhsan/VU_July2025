# import os, time, json, urllib.request, boto3

# cw = boto3.client("cloudwatch")
# NAMESPACE = os.environ.get("NAMESPACE", "Canary")
# TIMEOUT = float(os.environ.get("TIMEOUT_SECONDS", "10"))

# def load_sites():
#     """Read modules/sites.json; fall back to env TARGET_URL if JSON missing."""
#     here = os.path.dirname(__file__)
#     path = os.path.join(here, "sites.json")
#     try:
#         with open(path, "r") as f:
#             data = json.load(f)
#         return [s for s in data if "name" in s and "url" in s]
#     except Exception:
#         url = os.environ.get("TARGET_URL")
#         name = os.environ.get("SITE_NAME", "MainSite")
#         return [{"name": name, "url": url}] if url else []

# def probe(url: str):
#     start = time.time()
#     ok, latency_ms, status = 0, 0.0, None
#     try:
#         with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
#             status = r.status
#             latency_ms = (time.time() - start) * 1000.0
#             ok = 1 if 200 <= status < 300 else 0
#     except Exception:
#         latency_ms = (time.time() - start) * 1000.0
#         ok = 0
#     return ok, latency_ms, status

# def put(site: str, metric: str, value: float, unit: str | None = None):
#     datum = {
#         "MetricName": metric,
#         "Value": float(value),
#         "Dimensions": [{"Name": "SiteName", "Value": site}],
#     }
#     if unit:
#         datum["Unit"] = unit
#     cw.put_metric_data(Namespace=NAMESPACE, MetricData=[datum])

# def handler(event, context):
#     results = []
#     for s in load_sites():
#         name, url = s["name"], s["url"]
#         ok, lat, status = probe(url)
#         put(name, "Availability", ok)
#         put(name, "LatencyMs", lat, "Milliseconds")
#         print(f"site={name} url={url} ok={ok} status={status} latency_ms={round(lat,1)}")
#         results.append({"site": name, "ok": ok, "latency_ms": round(lat, 1), "status": status})
#     return {"results": results}
