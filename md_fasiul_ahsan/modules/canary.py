import os, time, urllib.request, json
import boto3

cw = boto3.client("cloudwatch")
URL = os.environ["TARGET_URL"]
NAMESPACE = os.environ.get("NAMESPACE", "Canary")

def _put(metric, value):
    cw.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[{"MetricName": metric, "Value": float(value)}]
    )

def handler(event, context):
    start = time.time()
    ok = 0
    latency_ms = 0.0
    try:
        with urllib.request.urlopen(URL, timeout=10) as r:
            latency_ms = (time.time() - start) * 1000.0
            ok = 1 if 200 <= r.status < 300 else 0
    except Exception:
        latency_ms = (time.time() - start) * 1000.0
        ok = 0

    # publish metrics
    _put("Availability", ok)
    _put("LatencyMs", latency_ms)

    return {
        "statusCode": 200 if ok else 500,
        "body": json.dumps({"ok": ok, "latency_ms": round(latency_ms, 1)})
    }
