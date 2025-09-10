<!-- # AWS CDK – Multi-Site Canary (Lambda + CloudWatch + Alarms + SNS + DynamoDB)

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
   } -->


# Advanced DevOps Project – AWS Monitoring & Automation

## 📌 Project Overview
This project demonstrates a complete **DevOps monitoring and alerting system** using AWS services.  

It integrates:  
- **CloudWatch** for metrics and alarms  
- **SNS** for notifications  
- **DynamoDB** for storing monitoring data  
- **Canary scripts (Python + Boto3)** for site health checks  
- **Infrastructure-as-Code (IaC)** with AWS CDK  

The goal of the project is to provide a **resilient monitoring architecture** that detects failures, sends alerts, and logs incidents automatically.

---

## 🏗️ Architecture Diagram
This diagram illustrates how all AWS services are connected:  
- Canary → CloudWatch → Alarms → SNS + DynamoDB  

*(Insert architecture diagram here)*  
![Architecture Diagram](D:\Victoria University\Block 3\Advance Project\VU_July2025\md_fasiul_ahsan\docs\screenshots\WebHealth Monitoring Architecture.png)

---

## 🎯 Goals
- Build a fully automated **monitoring and alerting system**  
- Deploy infrastructure using **AWS CDK**  
- Enable **site health checks** via Python canary scripts  
- Store incident logs in **DynamoDB** for historical analysis  
- Send **SNS notifications** on alarms and failures  

---

## 🔄 Project Flow & Data
1. **Canary Script** pings target websites.  
2. Metrics are pushed to **CloudWatch**.  
3. **CloudWatch Alarms** trigger when thresholds are breached.  
4. Alerts are sent to **SNS Topics** (Email/SMS).  
5. **DynamoDB** logs incidents for auditing.  

*(This screenshot should show your flow diagram with arrows between services.)*  
![Flow Diagram](images/flow.png)

---

## 📊 Dashboard & Alarms
- **Custom CloudWatch Dashboard** to track latency, availability, and error rates.  
- Alarms configured for:  
  - High latency  
  - Website downtime  
  - Failed health checks  

**Screenshots:**  
- Dashboard → metrics in real time  
- Alarm → example of triggered alert  

![CloudWatch Dashboard](images/dashboard.png)  
![CloudWatch Alarm](images/alarm.png)

---

## 🔒 Security & Non-Functional Requirements (NFRs)
To ensure system reliability and security:  
- IAM roles with **least-privilege access**  
- Encrypted storage for logs in DynamoDB  
- Monitoring scripts run in **isolated Lambda functions**  
- Scalability ensured through serverless architecture  

*(Screenshot: IAM Role details in AWS console)*  
![IAM Role](images/iam-role.png)

---

## ⚠️ Forced Failure Scenarios
To validate the monitoring system, **failure scenarios** were tested:  
1. **Shutting down EC2 instance** hosting the monitored site.  
2. **Blocking inbound traffic** to simulate downtime.  
3. **Artificial latency injection** in the canary script.  

Each failure correctly triggered alarms and **SNS notifications**.  

*(Screenshot: example of triggered alarm + notification)*  
![Failure Scenario Test](images/failure.png)

---

## 🚀 Deployment
The project was deployed using **AWS CDK** with the following steps:

```bash
# Synthesize CloudFormation templates
cdk synth

# Deploy the stack with verbose logging
cdk deploy -v
