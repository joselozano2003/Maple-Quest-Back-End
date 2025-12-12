# AWS Architecture

## Current Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   INTERNET                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS GLOBAL SERVICES                                │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                            S3 BUCKET                                    │    │
│  │                    maple-quest-images-xxx-region                        │    │
│  │                                                                         │    │
│  │  • Public Read Access                                                   │    │
│  │  • CORS Enabled                                                         │    │
│  │  • User Images Storage                                                  │    │
│  │  • Location Default Images                                              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        CLOUDWATCH LOGS                                  │    │
│  │                      /ecs/maple-quest-new                               │    │
│  │                                                                         │    │
│  │  • ECS Task Logs                                                        │    │
│  │  • 1 Week Retention                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                AWS REGION                                       │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                              VPC                                        │    │
│  │                           (2 AZs)                                       │    │
│  │                                                                         │    │
│  │  ┌─────────────────────┐              ┌─────────────────────┐           │    │
│  │  │   AVAILABILITY      │              │   AVAILABILITY      │           │    │
│  │  │      ZONE A         │              │      ZONE B         │           │    │
│  │  │                     │              │                     │           │    │
│  │  │  ┌───────────────┐  │              │  ┌───────────────┐  │           │    │
│  │  │  │ PUBLIC SUBNET │  │              │  │ PUBLIC SUBNET │  │           │    │
│  │  │  │               │  │              │  │               │  │           │    │
│  │  │  │ ┌───────────┐ │  │              │  │ ┌───────────┐ │  │           │    │
│  │  │  │ │    ALB    │ │  │              │  │ │    ALB    │ │  │           │    │
│  │  │  │ │ (Public)  │ │  │              │  │ │ (Public)  │ │  │           │    │
│  │  │  │ │ Port: 80  │ │  │              │  │ │ Port: 80  │ │  │           │    │
│  │  │  │ └───────────┘ │  │              │  │ └───────────┘ │  │           │    │
│  │  │  │       │       │  │              │  │       │       │  │           │    │
│  │  │  │       ▼       │  │              │  │       ▼       │  │           │    │
│  │  │  │ ┌───────────┐ │  │              │  │ ┌───────────┐ │  │           │    │
│  │  │  │ │ECS FARGATE│ │  │              │  │ │ECS FARGATE│ │  │           │    │
│  │  │  │ │   TASK    │ │  │              │  │ │   TASK    │ │  │           │    │
│  │  │  │ │           │ │  │              │  │ │           │ │  │           │    │
│  │  │  │ │Django App │ │  │              │  │ │Django App │ │  │           │    │
│  │  │  │ │Port: 8000 │ │  │              │  │ │Port: 8000 │ │  │           │    │
│  │  │  │ │Public IP  │ │  │              │  │ │Public IP  │ │  │           │    │
│  │  │  │ └───────────┘ │  │              │  │ └───────────┘ │  │           │    │
│  │  │  │       │       │  │              │  │       │       │  │           │    │
│  │  │  └───────┼───────┘  │              │  └───────┼───────┘  │           │    │
│  │  │          │          │              │          │          │           │    │
│  │  │          ▼          │              │          ▼          │           │    │
│  │  │  ┌───────────────┐  │              │  ┌───────────────┐  │           │    │
│  │  │  │     RDS DB    │  │              │  │     RDS DB    │  │           │    │
│  │  │  │ (PostgreSQL)  │  │              │  │ (PostgreSQL)  │  │           │    │
│  │  │  │               │  │              │  │               │  │           │    │
│  │  │  │ Public IP   ️  │  │              │  │ Public IP ️    │  │           │    │
│  │  │  │ Port: 5432    │  │              │  │ Port: 5432    │  │           │    │
│  │  │  │ 0.0.0.0/0   ️  │  │              │  │ 0.0.0.0/0     │  │           │    │
│  │  │  └───────────────┘  │              │  └───────────────┘  │           │    │
│  │  │                     │              │                     │           │    │
│  │  │  ┌───────────────┐  │              │  ┌───────────────┐  │           │    │
│  │  │  │PRIVATE SUBNET │  │              │  │PRIVATE SUBNET │  │           │    │
│  │  │  │   (Unused)    │  │              │  │   (Unused)    │  │           │    │
│  │  │  └───────────────┘  │              │  └───────────────┘  │           │    │
│  │  └─────────────────────┘              └─────────────────────┘           │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL ACCESS                                    │
│                                                                                 │
│  iOS App ─────────────────────────────────────────────────────────────────────┐ │
│                                                                               │ │
│  ┌─ HTTP Requests ──────────────────────────────────────────────────────────┐ │ │
│  │                                                                          │ │ │
│  │  • POST /auth/login/                                                     │ │ │
│  │  • GET /api/locations/                                                   │ │ │
│  │  • POST /api/locations/{id}/visit/                                       │ │ │
│  │  • POST /api/users/generate_upload_url/                                  │ │ │
│  │  • GET /api/users/friends/                                               │ │ │
│  │                                                                          │ │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │ │
│                                                                               │ │
│  ┌─ S3 Direct Upload ───────────────────────────────────────────────────────┐ │ │
│  │                                                                          │ │ │
│  │  • PUT https://bucket.s3.region.amazonaws.com/images/user/photo.jpg      │ │ │
│  │  • GET https://bucket.s3.region.amazonaws.com/locations/default.jpg      │ │ │
│  │                                                                          │ │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │ │
│                                                                               │ │
│  DBeaver (Dev Tool) ──────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─ Direct DB Connection   ───────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │  • Host: maple-quest-db.xxx.rds.amazonaws.com                              │ │
│  │  • Port: 5432                                                              │ │
│  │  • SECURITY RISK: Open to entire internet                                  │ │
│  │                                                                            │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### **Internet-Facing Components**

| Component                     | Access      | Security  | Purpose                             |
| ----------------------------- | ----------- | --------- | ----------------------------------- |
| **Application Load Balancer** | Public      |  Secure   | Routes HTTP traffic to ECS tasks    |
| **S3 Bucket**                 | Public Read |  Secure   | Serves images to iOS app            |
| **RDS Database**              | Public      | **RISK**  | Database access (should be private) |

### **VPC Resources**

| Resource                      | Subnet Type | Public IP | Security                 |
| ----------------------------- | ----------- | --------- | ------------------------ |
| **ECS Fargate Tasks**         | Public      | Yes       |  Protected by ALB        |
| **RDS PostgreSQL**            | Public      | Yes       |  **Exposed to internet** |
| **Application Load Balancer** | Public      | Yes       |  Properly configured     |

### **Data Flow**

```
1. iOS App → ALB (Port 80) → ECS Task (Port 8000) → RDS (Port 5432)
2. iOS App → S3 Bucket (Direct HTTPS) → Image Upload/Download
3. DBeaver → RDS (Direct Port 5432)  Security Risk
```

## Security Issues

### **Critical: Database Exposure**

- **Issue**: RDS database is publicly accessible from anywhere
- **Risk**: Potential unauthorized access to sensitive data
- **Current**: `0.0.0.0/0` can connect to port 5432
- **Impact**: High security vulnerability

### **Recommendations**

1. Move RDS to private subnets
2. Remove public accessibility
3. Use bastion host or VPN for development access
4. Implement proper security groups

## **Environment Variables**

### **ECS Task Environment**

```bash
SECRET_KEY=xxx
DEBUG=False
ALLOWED_HOSTS=*
S3_BUCKET_NAME=maple-quest-images-xxx-region
AWS_REGION=us-west-2
```

### **ECS Task Secrets (from AWS Secrets Manager)**

```bash
DB_NAME=maplequest
DB_USER=postgres
DB_PASSWORD=xxx (from secrets manager)
DB_HOST=maple-quest-db.xxx.rds.amazonaws.com
DB_PORT=5432
```

## **Scaling & Performance**

| Component     | Current      | Scaling                |
| ------------- | ------------ | ---------------------- |
| **ECS Tasks** | 1 instance   | Auto-scaling available |
| **RDS**       | t4g.micro    | Vertical scaling       |
| **ALB**       | Auto-scaling | AWS managed            |
| **S3**        | Unlimited    | AWS managed            |

## **Cost Optimization**

| Service           | Instance Type     | Cost Impact |
| ----------------- | ----------------- | ----------- |
| **ECS Fargate**   | 0.5 vCPU, 1GB RAM | ~$15/month  |
| **RDS**           | t4g.micro         | ~$15/month  |
| **ALB**           | Standard          | ~$20/month  |
| **S3**            | Pay per use       | Variable    |
| **Data Transfer** | Pay per GB        | Variable    |

## **Recommended Architecture**

For improved security, the database should be moved to private subnets:

```
Internet → ALB (Public) → ECS Tasks (Public) → RDS (Private)
                                            ↗ S3 (Global)
```

This eliminates direct internet access to the database while maintaining all functionality.
