# AWS CDK – Multi-Site Canary (Lambda + CloudWatch + Alarms + SNS + DynamoDB)

This project pings **three websites** on a schedule using an AWS **Lambda** canary and publishes custom **CloudWatch** metrics:

- `Availability` (1 = success, 0 = failure)
- `LatencyMs` (response time in milliseconds)

It also:

- Creates a **CloudWatch Dashboard** with charts and KPI tiles
- Sets **alarms per site** (Latency p95 and Availability)
- **Sends alarm notifications via SNS**
- **Logs each probe** into **DynamoDB** (site, timestamp, status, latency, HTTP code, reason)

> Region: **ap-southeast-2 (Sydney)**

---

## What the stack builds

- **Lambda**: `WebCanary` (Python 3.12) — reads `modules/sites.json`, fetches URLs, pushes metrics, writes to DynamoDB
- **EventBridge Rule** — runs the canary every **5 minutes**
- **CloudWatch Metrics** — Namespace `Canary`, dimension `SiteName`
- **CloudWatch Dashboard** — `3url-canary-dashboard` (charts, KPIs, alarm status)
- **CloudWatch Alarms** — per site:
  - `LatencyMs` (stat **p95**) > **2000 ms**
  - `Availability` (stat **Average**) < **1.0**
- **SNS Topic** — all alarms publish here (add your email subscription)
- **DynamoDB Table** — stores raw probe results  
  - **Partition key**: `site` (String)  
  - **Sort key**: `ts` (String, ISO8601 timestamp)  
  - (Optional) TTL attribute: `ttl` (Number, epoch seconds) if enabled in code

---

## Architecture

1. **EventBridge** triggers **Lambda** on a schedule.
2. Lambda loads sites from `md_fasiul_ahsan/modules/sites.json`, fetches each URL with a friendly User-Agent.
3. Lambda publishes:
   - `Availability` (1/0)
   - `LatencyMs` (milliseconds)
   - Dimension: `SiteName`
4. Lambda **puts an item** per site into **DynamoDB**:  
   ```json
   {
     "site": "Medilinks",
     "ts": "2025-08-22T10:15:30.123Z",
     "ok": 1,
     "latency_ms": 1345.7,
     "status": 200,
     "reason": "ok"
   }
