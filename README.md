
# Welcome to your CDK Python project!

# AWS CDK Hello Lambda (Python)

A tiny AWS CDK project that deploys a Python **Lambda** function and prints:

Hello Lambda
Md Fasiul Ahsan


## 🧭 Overview
- CDK (Python) creates one Lambda function.
- Handler: `HelloWorld.lambda_handler`
- Runtime: Python 3.12
- Region: set in `app.py` via `env=cdk.Environment(...)` (recommend `ap-southeast-2`).

---

## ✅ Prerequisites
- AWS account + AWS CLI configured (`aws configure`)
- Python 3.11/3.12
- Node.js (for CDK CLI)
- CDK CLI: `npm install -g aws-cdk`

---

## 🚀 Deploy (Step by step with screenshots)

### 1) Clone / open the project
![Project in VS Code](docs\screenshots\hello-world-test.jpg)

### 2) Create & activate virtual env, install dependencies
```bash
python -m venv .venv
# Git Bash:
source .venv/Scripts/activate
# PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Enjoy!
