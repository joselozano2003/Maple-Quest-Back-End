## DEPLOYMENT STEPS FOR ECS

### STEP 1: CREATE RDS DATABASE
1. Go to AWS RDS Console
2. Create Database → PostgreSQL
3. Settings:
   - DB identifier: myproject-db
   - Master username: postgres
   - Master password: [SAVE THIS!]
   - Instance class: db.t3.micro (or db.t4g.micro)
   - Storage: 20 GB
   - VPC: Create new or use existing
   - Public access: No
   - Database name: myproject_db
4. Security Group:
   - Create new security group: myproject-rds-sg
   - Note the RDS endpoint after creation

### STEP 2: STORE SECRETS IN AWS SECRETS MANAGER
1. Go to AWS Secrets Manager
2. Store a new secret → Other type of secret
3. Add key-value pairs:
   - SECRET_KEY: [generate a long random string]
   - DB_NAME: myproject_db
   - DB_USER: postgres
   - DB_PASSWORD: [your RDS password]
   - DB_HOST: [your-rds-endpoint.region.rds.amazonaws.com]
   - DB_PORT: 5432
   - DEBUG: False
   - ALLOWED_HOSTS: *
4. Secret name: myproject/production
5. Note the ARN for each secret

### STEP 3: CREATE ECR REPOSITORY
1. Go to Amazon ECR Console
2. Create repository
3. Repository name: myproject
4. Note the repository URI

#### Build and push Docker image locally:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -t myproject .
docker tag myproject:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/myproject:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/myproject:latest

### STEP 4: CREATE IAM ROLES

#### A. ECS Task Execution Role (ecsTaskExecutionRole)
1. Go to IAM → Roles → Create role
2. Trusted entity: AWS service → Elastic Container Service → Elastic Container Service Task
3. Attach policies:
   - AmazonECSTaskExecutionRolePolicy
   - SecretsManagerReadWrite (or create custom policy with only read access)
4. Role name: ecsTaskExecutionRole

Custom policy for Secrets Manager (more secure):
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:region:account:secret:myproject/*"
    }
  ]
}

#### B. ECS Task Role (ecsTaskRole)
1. Create role → AWS service → Elastic Container Service → Elastic Container Service Task
2. Attach policies as needed (S3, SES, etc.)
3. Role name: ecsTaskRole

### STEP 5: CREATE ECS CLUSTER
1. Go to Amazon ECS Console
2. Create Cluster
3. Cluster name: myproject-cluster
4. Infrastructure: AWS Fargate
5. Create

### STEP 6: CREATE ALB (Application Load Balancer)
1. Go to EC2 → Load Balancers → Create Load Balancer
2. Application Load Balancer
3. Settings:
   - Name: myproject-alb
   - Scheme: Internet-facing
   - IP address type: IPv4
   - VPC: Same as RDS
   - Subnets: Select at least 2 AZs
4. Security group:
   - Create new: myproject-alb-sg
   - Inbound: HTTP (80), HTTPS (443) from 0.0.0.0/0
5. Listener: HTTP:80
6. Target group:
   - Create new: myproject-tg
   - Target type: IP
   - Protocol: HTTP
   - Port: 8000
   - Health check path: /health/
   - Health check interval: 30 seconds
7. Create

### STEP 7: CREATE CLOUDWATCH LOG GROUP
1. Go to CloudWatch → Log groups
2. Create log group
3. Name: /ecs/myproject
4. Retention: 7 days (or your preference)

### STEP 8: CREATE TASK DEFINITION
1. Go to ECS → Task Definitions → Create new Task Definition
2. Family: myproject-task
3. Launch type: Fargate
4. Operating system: Linux
5. Task size:
   - CPU: 0.5 vCPU (512)
   - Memory: 1 GB (1024)
6. Task execution role: ecsTaskExecutionRole
7. Task role: ecsTaskRole
8. Container:
   - Name: django-app
   - Image URI: YOUR_ACCOUNT_ID.dkr.ecr.region.amazonaws.com/myproject:latest
   - Port mappings: 8000 TCP
   - Environment variables: Use Secrets Manager ARNs
   - Log configuration:
     - Log driver: awslogs
     - Log group: /ecs/myproject
     - Region: us-east-1
     - Stream prefix: django
   - Health check:
     - Command: CMD-SHELL,curl -f http://localhost:8000/health/ || exit 1
     - Interval: 30
     - Timeout: 5
     - Retries: 3
     - Start period: 60

#### OR use the task-definition.json file and register via CLI:
aws ecs register-task-definition --cli-input-json file://task-definition.json

### STEP 9: UPDATE SECURITY GROUPS

#### RDS Security Group (myproject-rds-sg)
Inbound Rules:
- Type: PostgreSQL (5432)
- Source: myproject-ecs-sg (ECS security group)

#### ECS Security Group (myproject-ecs-sg - create new)
Inbound Rules:
- Type: Custom TCP (8000)
- Source: myproject-alb-sg (ALB security group)

Outbound Rules:
- All traffic to 0.0.0.0/0

#### ALB Security Group (myproject-alb-sg)
Inbound Rules:
- Type: HTTP (80), Source: 0.0.0.0/0
- Type: HTTPS (443), Source: 0.0.0.0/0

Outbound Rules:
- Type: Custom TCP (8000)
- Destination: myproject-ecs-sg

### STEP 10: CREATE ECS SERVICE
1. Go to ECS → Clusters → myproject-cluster → Services → Create
2. Launch type: Fargate
3. Task Definition: myproject-task (latest)
4. Service name: myproject-service
5. Number of tasks: 2 (for high availability)
6. Deployment options:
   - Rolling update
   - Minimum: 50%
   - Maximum: 200%
7. Networking:
   - VPC: Same as RDS and ALB
   - Subnets: Private subnets (recommended) or public
   - Security group: myproject-ecs-sg
   - Public IP: Enabled (if using public subnets)
8. Load balancer:
   - Type: Application Load Balancer
   - Load balancer: myproject-alb
   - Target group: myproject-tg
   - Health check grace period: 60 seconds
9. Service auto scaling (optional):
   - Minimum: 2
   - Maximum: 10
   - Metric: CPU or Memory
   - Target: 70%
10. Create service

### STEP 11: RUN DATABASE MIGRATIONS

#### Option A: Use ECS Exec (recommended)
1. Enable ECS Exec on service
2. Connect to running task:
aws ecs execute-command \
  --cluster myproject-cluster \
  --task TASK_ID \
  --container django-app \
  --interactive \
  --command "/bin/bash"

3. Run migrations:
python manage.py migrate
python manage.py createsuperuser

#### Option B: Run one-off task
aws ecs run-task \
  --cluster myproject-cluster \
  --task-definition myproject-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":[{"name":"django-app","command":["python","manage.py","migrate"]}]}'

#### Option C: Use AWS Systems Manager Session Manager
Requires additional setup but provides secure shell access

### STEP 12: TEST DEPLOYMENT
1. Get ALB DNS name from EC2 → Load Balancers
2. Test endpoints:
   curl http://your-alb-dns.region.elb.amazonaws.com/health/
   curl http://your-alb-dns.region.elb.amazonaws.com/admin/

3. Check CloudWatch Logs:
   /ecs/myproject → django/django-app/TASK_ID

### STEP 13: SETUP CUSTOM DOMAIN (Optional)
1. Go to Route 53
2. Create hosted zone for your domain
3. Create A record:
   - Name: api.yourdomain.com
   - Type: A - Alias
   - Alias target: Your ALB
4. Setup SSL certificate in ACM
5. Add HTTPS listener to ALB

### STEP 14: SETUP CI/CD (Optional)
1. Go to CodePipeline → Create pipeline
2. Source: GitHub/CodeCommit/GitLab
3. Build: CodeBuild (use buildspec.yml)
4. Deploy: ECS (cluster + service)
5. Every git push will trigger auto-deployment

### MONITORING & MAINTENANCE

#### View logs:
aws logs tail /ecs/myproject --follow

#### Update service with new image:
aws ecs update-service \
  --cluster myproject-cluster \
  --service myproject-service \
  --force-new-deployment

#### Scale service:
aws ecs update-service \
  --cluster myproject-cluster \
  --service myproject-service \
  --desired-count 4

#### Stop task:
aws ecs stop-task \
  --cluster myproject-cluster \
  --task TASK_ID

#### View service events:
aws ecs describe-services \
  --cluster myproject-cluster \
  --services myproject-service
"""

### COST ESTIMATION (Monthly)

#### Fargate (2 tasks, 0.5 vCPU, 1GB RAM):
- CPU: 2 tasks × 0.5 vCPU × $0.04048/hour × 730 hours = ~$59
- Memory: 2 tasks × 1GB × $0.004445/GB/hour × 730 hours = ~$6.50
- Total Fargate: ~$65.50/month

#### RDS (db.t3.micro, 20GB storage):
- Instance: $0.017/hour × 730 hours = ~$12.50
- Storage: 20GB × $0.115/GB = ~$2.30
- Total RDS: ~$14.80/month

#### Application Load Balancer:
- ALB: $0.0225/hour × 730 hours = ~$16.50
- LCU: varies by traffic (~$5-20/month)
- Total ALB: ~$21.50+/month

#### Other services:
- ECR: First 500MB free, then $0.10/GB/month
- CloudWatch Logs: First 5GB free, then $0.50/GB
- Secrets Manager: $0.40/secret/month = ~$3.20
- NAT Gateway (if using private subnets): ~$32/month

#### TOTAL ESTIMATED COST: ~$110-150/month

#### Cost optimization tips:
- Use Spot instances for non-critical tasks
- Use Fargate Savings Plans for 30-50% discount
- Use private subnets with VPC endpoints instead of NAT Gateway
- Use RDS Reserved Instances for 40% discount
- Enable ALB idle timeout and connection draining
"""

### TROUBLESHOOTING

#### Issue 1: Tasks failing health checks
- Check CloudWatch logs for errors
- Verify health check endpoint /health/ is accessible
- Increase health check grace period
- Check security groups allow ALB → ECS traffic on port 8000

#### Issue 2: Cannot connect to RDS
- Verify RDS security group allows inbound from ECS security group
- Check RDS endpoint is correct in Secrets Manager
- Ensure tasks are in same VPC as RDS
- Test connection using psql from ECS task

#### Issue 3: Tasks start then stop immediately
- Check CloudWatch logs for startup errors
- Verify all environment variables are set correctly
- Check Secrets Manager ARNs are correct
- Verify IAM roles have correct permissions

#### Issue 4: Static files not loading
- Ensure collectstatic runs in Dockerfile
- Check WhiteNoise is in MIDDLEWARE
- Verify STATIC_ROOT is set correctly

#### Issue 5: 502 Bad Gateway from ALB
- Check ECS tasks are running and healthy
- Verify target group health checks are passing
- Check security groups allow traffic
- Review CloudWatch logs for application errors

#### Issue 6: Database migrations not applied
- Run migrations manually using ECS Exec
- Or create a separate task definition for migrations
- Check database connectivity from ECS tasks

### Debug commands:
#### Check task status:
aws ecs describe-tasks --cluster myproject-cluster --tasks TASK_ID

#### View logs:
aws logs get-log-events \
  --log-group-name /ecs/myproject \
  --log-stream-name django/django-app/TASK_ID

#### Test RDS connectivity:
aws ecs execute-command \
  --cluster myproject-cluster \
  --task TASK_ID \
  --container django-app \
  --interactive \
  --command "python manage.py dbshell"