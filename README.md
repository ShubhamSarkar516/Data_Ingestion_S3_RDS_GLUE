
# 📊 Data Ingestion from S3 to RDS with Fallback to AWS Glue (Dockerized Python App)

This project implements a **resilient data ingestion pipeline** that reads CSV data from an **Amazon S3 bucket**, attempts to ingest it into an **RDS MySQL database**, and falls back to **AWS Glue** for cataloging if the database insertion fails. It uses **Docker** to containerize the pipeline for easy deployment.

---

## ✅ Features

- ⬇️ Download CSV file from Amazon S3
- 🐬 Insert data into AWS RDS (MySQL-compatible)
- 🔁 Automatic fallback to AWS Glue if RDS fails
- 🐳 Dockerized for portability and consistency
- 🔒 Uses `.env` file for secrets (no hardcoded credentials)

---

## 🧰 Technology Stack

| Tool/Service       | Purpose                                |
|--------------------|----------------------------------------|
| **Python 3.9+**     | Main scripting language                |
| **Docker**         | Containerization of app                |
| **AWS S3**         | CSV file storage                       |
| **AWS RDS**        | Target database                        |
| **AWS Glue**       | Fallback schema catalog                |
| **boto3**          | AWS SDK for Python                     |
| **SQLAlchemy**     | RDS database interaction               |
| **Pandas**         | Data transformation                    |
| **.env file**      | Secure credentials & config management |

---

## 📂 Directory Structure

```
s3-to-rds-glue-fallback/
├── main.py
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
```

---

## ⚙️ Setup Instructions

### 1️⃣ Launch & Access EC2 Instance

```bash
ssh -i your-key.pem ubuntu@<your-ec2-ip>
```

### 2️⃣ Prepare Your Environment

```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev docker.io unzip mysql-client git curl -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
logout  # Re-login after this
```

### 3️⃣ Install AWS CLI & Configure

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws configure
# Provide: Access Key, Secret Key, Region (e.g., us-east-1), Output format
```

---

## ☁️ AWS Resources Setup

### 📦 S3 Bucket

- Bucket Name: `my-data-ingestion-bucket`
- File Uploaded: `people.csv`

```csv
id,name,email
1,Shubham,shubham@example.com
2,Alice,alice@example.com
```

### 🐬 RDS MySQL Setup

```sql
CREATE DATABASE data_ingestion_db;
USE data_ingestion_db;
CREATE TABLE people (
  id INT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(100)
);
```

> Username: `admin`, Password: `yourpassword`, Port: `3306`

### 🔎 AWS Glue Setup

- Glue Database: `my_glue_db`
- No need to pre-create table – it’s generated on fallback

---

## 🔐 .env File (Secrets Example)

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

S3_BUCKET=my-data-ingestion-bucket
S3_KEY=people.csv

RDS_HOST=mydb-instance.rds.amazonaws.com
RDS_PORT=3306
RDS_DB=data_ingestion_db
RDS_USER=admin
RDS_PASSWORD=shubham123456
RDS_TABLE=people

GLUE_DB=my_glue_db
GLUE_TABLE=people_glue
GLUE_S3_LOCATION=s3://my-data-ingestion-bucket/
```

---

## 🐳 Docker Usage

### 🔧 Build the Image

```bash
docker build -t s3-to-rds-glue-app .
```

### 🚀 Run the Container

```bash
docker run --env-file .env s3-to-rds-glue-app
```

If permission denied:

```bash
sudo docker run --env-file .env s3-to-rds-glue-app
```

---

## ✅ Output Validation

- ✅ `SELECT * FROM people;` in RDS DB
- ✅ Check AWS Glue > Tables → `people_glue` (if fallback occurred)
- ✅ Container logs will show fallback or success status

---

## 🧹 Cleanup

```bash
# Delete EC2 instance, S3 files, RDS instance, and Glue table if no longer needed
```

---

## 📁 .gitignore

```
.env
__pycache__/
*.pyc
*.pyo
*.log
*.zip
*.DS_Store
venv/
```

---

## 📌 Notes

- Avoid pushing `.env` to GitHub
- Use Secrets Manager/SSM in production
- Monitor Glue/AWS billing
- Rotate keys after testing
