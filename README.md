# Cloud Computing MiniLab Project

This project demonstrates a cloud-native system using:

- ECS (Elastic Compute Service)
- Function Compute (Serverless Functions)
- OSS (Object Storage Service)
- Docker-based deployment

# 1. System Overview

The system consists of:

- Cloud Server (ECS): Runs the main application
- Function Compute (FC): Executes backend logic
- OSS: Stores files and data
- .env configuration: Manages sensitive credentials securely

# 2. Cloud Environment Setup

## Step 1: Create ECS Cloud Server

1. Log in to Alibaba Cloud Console
2. Create an ECS instance
3. Recommended configuration:
   - OS: Ubuntu / CentOS
   - Open ports: 22, 80, 5000, 5001, 8080

## Step 2: Enable Cloud Services

Enable the following services:

- Function Compute (FC)
- Object Storage Service (OSS)

# 3. Function Compute Setup

## Step 1: Create Functions

Create three functions:

1. result_update Function
2. processing Function
3. submission_event Function

## Step 2: Deploy Code

For each function:

- Create function in FC console
- Select runtime (Python 3.8)
- Copy code into editor
- Replace URL and DATA references correctly
- Deploy and test function

# 4. OSS Setup

## Step 1: Create OSS Bucket

- Create bucket in OSS console
- Configure:
  - Region
  - Storage class: Standard
  - Access: Private

## Step 2: Get Credentials

- AccessKey ID
- AccessKey Secret
- Bucket Name
- Endpoint

Do not expose credentials in public repositories.

# 5. Environment Configuration

Modify .env in project root:

```env
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-your-region.aliyuncs.com
```

# 6. Deployment Guide (ECS Server)

## Step 1: Connect to Server

```bash
ssh root@<your-server-ip>
```

## Step 2: Install Docker

```bash
curl -fsSL https://get.docker.com | bash
systemctl start docker
systemctl enable docker
```

## Step 3: Install Docker Compose

```bash
apt update
apt install docker-compose-plugin -y
```

Check version:

```bash
docker compose version
```

## Step 4: Upload Project

```bash
git clone <your-repo-url>
```

OR

```bash
scp -r MINILAB root@<server-ip>:/root/
```

## Step 5: Run Project

```bash
cd MINILAB
docker compose build
docker compose up -d
```

Check running containers:

```bash
docker ps
```

Logs:

```bash
docker compose logs -f
```

# 7. Usage Guide

Access system via:

```
https://<your-public-ip>:8080
```

Steps:

* Ensure port 8080 is open in security group
* Ensure containers are running
* Visit the URL in browser

If issues occur:

* Check firewall rules
* Check Docker status
* Ensure service binds to 0.0.0.0:8080

```
```
