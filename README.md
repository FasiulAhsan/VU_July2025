
# Welcome to your CDK Python project!

# AWS CDK – Website Canary (Single URL)

A tiny CDK project that deploys one Python **Lambda** to monitor **https://medilinks.com.au/** every 5 minutes and publishes:
- **Availability** (1=success, 0=failure)
- **LatencyMs** (milliseconds)

## Overview
- Lambda handler: `canary.handler`
- Schedule: EventBridge rule (every 5 min)
- Metrics namespace: `Canary`, dimension: `SiteName=Medilinks`
- Region set in `app.py` (use `ap-southeast-2`)

## Prerequisites
- Python 3.11/3.12, AWS CLI configured, Node.js + CDK (`npm i -g aws-cdk`)

## Setup & Deploy
```bash
python -m venv .venv
# Git Bash:
source .venv/Scripts/activate
# PowerShell: .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
# first time per account/region:
cdk bootstrap aws://<account-id>/ap-southeast-2
cdk synth
cdk deploy


Enjoy!
