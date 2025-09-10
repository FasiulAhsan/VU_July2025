import os, time, json, urllib.request, boto3
from datetime import datetime

# --- CloudWatch client (metrics) ---
cw = boto3.client("cloudwatch")

# --- Optional DynamoDB (enabled if TABLE_NAME is set in env by the stack) ---
TABLE_NAME = os.environ.get("TABLE_NAME")
ddb = boto3.resource("dynamodb") if TABLE_NAME else None
table = ddb.Table(TABLE_NAME) if ddb else None

# --- Config from env ---
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
    """Run once per schedule; publish Availability + LatencyMs per SiteName; optionally store to DynamoDB."""
    results = []
    sites = load_sites()
    print("loaded_sites:", [s["name"] for s in sites])

    # Common timestamp for all items in this run
    ping_time_iso = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    # Optional TTL (~14 days) if your table's TTL attribute is enabled
    ttl_epoch = int(time.time()) + 14 * 24 * 60 * 60

    for s in sites:
        name, url = s["name"], s["url"]
        ok, lat_ms, status, reason = probe(url)

        # --- Publish both metrics in one call ---
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

        # --- Write one item per site to DynamoDB (if configured) ---
        if table:
            item = {
                "SiteName": name,                              # PK
                "PingTime": ping_time_iso,                     # SK (ISO timestamp)
                "Ok": int(ok),
                "LatencyMs": int(round(lat_ms)),               # store as int to avoid float/Decimal issues
                "Status": int(status) if status is not None else 0,
                "Reason": reason,
                "TtlEpoch": ttl_epoch,                         # works with table TTL if enabled
            }
            try:
                table.put_item(Item=item)
            except Exception as e:
                print(f"dynamodb_put_error site={name} err={type(e).__name__}")

        # --- Structured log for CloudWatch Logs ---
        print(json.dumps({
            "site": name, "url": url, "ok": ok,
            "status": status, "latency_ms": round(lat_ms, 1),
            "reason": reason, "ping_time": ping_time_iso
        }))

        results.append({"site": name, "ok": ok, "latency_ms": round(lat_ms, 1)})

    return {"results": results}
