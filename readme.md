## Prerequisites:

- Docker and Docker Compose installed on your machine.
- Python 3.8 or higher installed (for local development).
- AWS CLI installed and configured (for AWS interactions, probably unnecessary for most).

**Note for Apple Silicon (M1/M2/M3) Users:**

- The local `Dockerfile` works natively on ARM64 (Apple Silicon)
- For AWS deployment, use `Dockerfile.production` which targets AMD64

## Initialization Steps:

1. Ensure that all prerequisites are met
2. Copy the contents from `.env.example` and create a new file named `.env` in the root directory of this repository
3. Execute the command `make up` in the terminal in the root directory of this repository, to start up the server
4. When done, execute the command `make down` in the terminal in the root directory of this repository, to shut down the server

## Connecting to AWS

- Make sure you have the AWS CLI installed and configured with the proper credentials.
- AWS connection is mostly for deploying the infrastructure using AWS CDK and for pushing Docker images to Amazon ECR.

## AI-Generated Documentation

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/joselozano2003/Maple-Quest-Back-End)

## S3 Image Storage

The application uses different storage solutions for local development and production:

### Local Development (MinIO)

- **Storage**: MinIO S3-compatible server running in Docker
- **Access**: `http://localhost:9000`
- **Console**: `http://localhost:9001` (minioadmin/minioadmin123)
- **URLs**: `http://localhost:9000/maple-quest-images/...`
- **Benefits**: No AWS costs, offline development, faster uploads

### Production (AWS S3)

- **Storage**: Real AWS S3 bucket
- **Access**: HTTPS with AWS infrastructure
- **Benefits**: Scalable, reliable, global CDN

### Upload Workflow:

1. **Get Upload URL**: Call `/api/users/generate_upload_url/` with filename
2. **Upload Image**: Use the `upload_url` to PUT the image file
3. **Use Public URL**: Use the `public_url` in your visit images

### Environment Differences:

| Feature          | Local (MinIO)            | Production (AWS S3)                          |
| ---------------- | ------------------------ | -------------------------------------------- |
| **Base URL**     | `http://localhost:9000`  | `https://<bucket>.s3.<region>.amazonaws.com` |
| **Credentials**  | minioadmin/minioadmin123 | AWS IAM (automatic)                          |
| **Console**      | http://localhost:9001    | AWS S3 Console                               |
| **Cost**         | Free                     | Pay per usage                                |
| **Performance**  | Local network speed      | Global CDN                                   |
| **Availability** | Local only               | 99.999999999%                                |

### Deployment:

**Local Development:**

```bash
make up  # Starts MinIO automatically
```

**Production Deployment:**

```bash
cd maple-quest-cdk
npm install
npm run build
npm run cdk deploy  # Creates real S3 bucket
```

### Health Check

```bash
GET /health/
```

Returns server health status and database connectivity.

## Connecting to the Database

- The application is configured to connect to a PostgreSQL database in RDS.
- Reach out to Lozano for the database credentials and connection details, but its not needed, you can run the app locally with the local Postgres instance defined in the docker-compose file.

## API Quick Reference

### Image & Photo Management

| Endpoint                          | Method | Auth | Description                               |
| --------------------------------- | ------ | ---- | ----------------------------------------- |
| `/api/images/`                    | GET    | ✅   | Get all YOUR uploaded images              |
| `/api/images/{id}/`               | GET    | ✅   | Get a specific image                      |
| `/api/locations/{id}/images/`     | GET    | ❌   | Get all images for a location (all users) |
| `/api/visits/{id}/`               | GET    | ✅   | Get a visit with all its images           |
| `/api/locations/{id}/visit/`      | POST   | ✅   | Visit location and add images             |
| `/api/users/generate_upload_url/` | POST   | ✅   | Get S3 presigned URL for upload           |

### Location Management

| Endpoint                     | Method | Auth | Description                    |
| ---------------------------- | ------ | ---- | ------------------------------ |
| `/api/locations/`            | GET    | ❌   | Get all locations              |
| `/api/locations/{id}/`       | GET    | ❌   | Get specific location          |
| `/api/locations/`            | POST   | ✅   | Create new location            |
| `/api/locations/{id}/visit/` | POST   | ✅   | Visit a location               |
| `/api/visits/`               | GET    | ✅   | Get all your visits            |
| `/api/visits/{id}/`          | GET    | ✅   | Get specific visit with images |

### User & Profile

| Endpoint               | Method | Auth | Description           |
| ---------------------- | ------ | ---- | --------------------- |
| `/auth/register/`      | POST   | ❌   | Register new user     |
| `/auth/login/`         | POST   | ❌   | Login user            |
| `/auth/profile/`       | GET    | ✅   | Get your profile      |
| `/auth/profile/`       | PUT    | ✅   | Update your profile   |
| `/auth/token/refresh/` | POST   | ❌   | Refresh JWT token     |
| `/api/users/me/`       | GET    | ✅   | Get current user      |
| `/api/users/friends/`  | GET    | ✅   | Get your friends list |

### Friend System

| Endpoint                            | Method | Auth | Description           |
| ----------------------------------- | ------ | ---- | --------------------- |
| `/api/friend-requests/add_friend/`  | POST   | ✅   | Send friend request   |
| `/api/friend-requests/`             | GET    | ✅   | Get friend requests   |
| `/api/friend-requests/{id}/accept/` | POST   | ✅   | Accept friend request |
| `/api/friend-requests/{id}/reject/` | POST   | ✅   | Reject friend request |

## Response Status Codes

| Code | Meaning      | Common Causes                           |
| ---- | ------------ | --------------------------------------- |
| 200  | Success      | Request completed successfully          |
| 201  | Created      | Resource created successfully           |
| 400  | Bad Request  | Invalid data or missing required fields |
| 401  | Unauthorized | Missing or invalid authentication token |
| 403  | Forbidden    | Not allowed to access this resource     |
| 404  | Not Found    | Resource doesn't exist                  |
| 500  | Server Error | Internal server error                   |

## Authentication Notes

- All authenticated endpoints require the `Authorization: Bearer <token>` header
- Access tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Use `/auth/token/refresh/` to get a new access token
- Tokens are returned on registration and login
