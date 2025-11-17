## Prerequisites:

- Docker and Docker Compose installed on your machine.
- Python 3.8 or higher installed (for local development).
- AWS CLI installed and configured (for AWS interactions, probably unnecessary for most).

## General:

- To start the app

`make up`

- To shut down the app

`make down`

## Running Django commands

- As the app is running inside a docker container, to run django commands you need to run them through docker-compose. For example, to run migrations:

`docker-compose exec web python manage.py migrate`

- To create a superuser:
  `docker-compose exec web python manage.py createsuperuser`

- Just run:
  `docker-compose exec web python manage.py <command>`

**Note:** After adding first_name and last_name fields, you'll need to run migrations:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Connecting to AWS

- Make sure you have the AWS CLI installed and configured with the proper credentials.
- AWS connection is mostly for deploying the infrastructure using AWS CDK and for pushing Docker images to Amazon ECR.
- The later will be added in future PR where I will add GH actions for CI/CD.

## Documentation

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/joselozano2003/Maple-Quest-Back-End)

## API Endpoints

### Authentication

All authentication endpoints use JWT tokens for secure access.

#### User Registration

```bash
POST /auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_no": "1234567890"
}
```

As there is no UI screen for creating users, you can run the following command on the terminal to create a user:

```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_no": "1234567890"
  }'
```

**Note:** `first_name`, `last_name`, and `phone_no` are optional fields. You can register with just email and password:

```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "simple@example.com", "password": "password123"}'
```

**Response:**

```json
{
  "user": {
    "user_id": "abc123-def456",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_no": "1234567890",
    "points": 0,
    "profile_pic_url": "",
    "created_at": "2025-11-05T21:10:32.998848Z"
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": "User registered successfully"
}
```

#### User Login

```bash
POST /auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "user": {
    "user_id": "abc123-def456",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_no": "1234567890",
    "points": 0,
    "profile_pic_url": "",
    "created_at": "2025-11-05T21:10:32.998848Z"
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": "Login successful"
}
```

#### Get User Profile

```bash
GET /auth/profile/
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "user_id": "abc123-def456",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_no": "1234567890",
  "points": 0,
  "profile_pic_url": "",
  "created_at": "2025-11-05T21:10:32.998848Z"
}
```

#### Update User Profile

```bash
PUT /auth/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Johnny",
  "last_name": "Smith",
  "phone_no": "9876543210",
  "profile_pic_url": "https://example.com/new-profile.jpg"
}
```

**Partial Updates:** You can update individual fields:

```bash
# Update only name
curl -X PUT http://localhost:8000/auth/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"first_name": "Johnny", "last_name": "Smith"}'

# Update only profile picture
curl -X PUT http://localhost:8000/auth/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"profile_pic_url": "https://example.com/new-avatar.jpg"}'
```

#### Refresh JWT Token

```bash
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Location Endpoints

#### Get All Locations (No Authentication Required)

```bash
GET /api/locations/
```

#### Get Specific Location (No Authentication Required)

```bash
GET /api/locations/{location_id}/
```

#### Create Location (Authentication Required)

```bash
POST /api/locations/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Central Park",
  "latitude": "40.785091",
  "longitude": "-73.968285",
  "description": "A large public park in Manhattan",
  "points": 50
}
```

#### Visit Location (Authentication Required)

```bash
POST /api/locations/{location_id}/visit/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "note": "Amazing place to visit!",
  "images": [
    {
      "image_url": "https://example.com/photo1.jpg",
      "description": "Beautiful sunset view"
    },
    {
      "image_url": "https://example.com/photo2.jpg",
      "description": "Great hiking trail"
    }
  ]
}
```

**Response:**

```json
{
  "message": "Location visited successfully",
  "visit": {
    "id": 1,
    "user": "user123",
    "location": "loc456",
    "visited_at": "2024-11-16T10:30:00Z",
    "note": "Amazing place to visit!"
  },
  "images": [
    {
      "id": 1,
      "visit": 1,
      "image_url": "https://example.com/photo1.jpg",
      "description": "Beautiful sunset view",
      "likes": 0
    }
  ],
  "points_earned": 50,
  "total_points": 150
}
```

### Visit Endpoints

#### Get All Your Visits (Authentication Required)

```bash
GET /api/visits/
Authorization: Bearer <access_token>
```

**Response includes images for each visit:**

```json
[
  {
    "id": 1,
    "user": "user123",
    "location": "loc456",
    "visited_at": "2024-11-16T10:30:00Z",
    "note": "Amazing place to visit!",
    "images": [
      {
        "id": 1,
        "visit": 1,
        "image_url": "https://example.com/photo1.jpg",
        "description": "Beautiful sunset view",
        "likes": 5
      }
    ]
  }
]
```

#### Get Specific Visit (Authentication Required)

```bash
GET /api/visits/{visit_id}/
Authorization: Bearer <access_token>
```

### Friend System Endpoints

#### Add Friend by Email or Phone (Authentication Required)

```bash
POST /api/friend-requests/add_friend/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "friend@example.com"
}
```

OR

```bash
{
  "phone_no": "1234567890"
}
```

**Response:**

```json
{
  "message": "Friend request sent successfully",
  "friend_request": {
    "id": 1,
    "from_user": "user123",
    "to_user": "user456",
    "status": "pending",
    "created_at": "2024-11-16T10:30:00Z"
  }
}
```

#### Accept Friend Request (Authentication Required)

```bash
POST /api/friend-requests/{friend_request_id}/accept/
Authorization: Bearer <access_token>
```

#### Reject Friend Request (Authentication Required)

```bash
POST /api/friend-requests/{friend_request_id}/reject/
Authorization: Bearer <access_token>
```

#### Get Friend Requests (Authentication Required)

```bash
GET /api/friend-requests/
Authorization: Bearer <access_token>
```

#### Get Friends List (Authentication Required)

```bash
GET /api/users/friends/
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "friends": [
    {
      "user_id": "friend123",
      "email": "friend1@example.com",
      "first_name": "Alice",
      "last_name": "Johnson",
      "phone_no": "1234567890",
      "points": 150,
      "profile_pic_url": "https://example.com/profile1.jpg",
      "created_at": "2024-11-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

### Image Endpoints

#### Get Images from Your Visits (Authentication Required)

```bash
GET /api/images/
Authorization: Bearer <access_token>
```

### User Profile Endpoints

#### Get Current User Profile (Authentication Required)

```bash
GET /api/users/me/
Authorization: Bearer <access_token>
```

#### Generate S3 Upload URL (Authentication Required)

```bash
POST /api/users/generate_upload_url/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "filename": "my-photo.jpg"
}
```

**Example with curl:**

```bash
curl -X POST http://localhost:8000/api/users/generate_upload_url/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"filename": "test.jpg"}'
```

**Response (Local Development with MinIO):**

```json
{
  "upload_url": "http://localhost:9000/maple-quest-images/images/user123/abc12345.jpg?AWSAccessKeyId=minioadmin&Signature=...",
  "public_url": "http://localhost:9000/maple-quest-images/images/user123/abc12345.jpg",
  "file_key": "images/user123/abc12345.jpg",
  "expires_in": 3600
}
```

**Response (Production with AWS S3):**

```json
{
  "upload_url": "https://maple-quest-images-123456789-us-west-2.s3.amazonaws.com/images/user123/abc12345.jpg?X-Amz-Algorithm=...",
  "public_url": "https://maple-quest-images-123456789-us-west-2.s3.amazonaws.com/images/user123/abc12345.jpg",
  "file_key": "images/user123/abc12345.jpg",
  "expires_in": 3600
}
```

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
- **URLs**: `https://bucket-name.s3.region.amazonaws.com/...`
- **Benefits**: Scalable, reliable, global CDN

### Upload Workflow:

1. **Get Upload URL**: Call `/api/users/generate_upload_url/` with filename
2. **Upload Image**: Use the `upload_url` to PUT the image file
3. **Use Public URL**: Use the `public_url` in your visit images

**iOS Upload Example:**

```swift
// 1. Get presigned URL from your API
let response = await getUploadURL(filename: "photo.jpg")

// 2. Upload image using the presigned URL
let uploadURL = URL(string: response.upload_url)!
var request = URLRequest(url: uploadURL)
request.httpMethod = "PUT"
request.setValue("image/jpeg", forHTTPHeaderField: "Content-Type")
request.httpBody = imageData

let (_, uploadResponse) = try await URLSession.shared.data(for: request)

// 3. Use the public_url in your visit API call
let visitData = [
    "note": "Beautiful place!",
    "images": [
        [
            "image_url": response.public_url,
            "description": "Amazing view"
        ]
    ]
]
```

**Test Upload with curl:**

```bash
# 1. Get upload URL
RESPONSE=$(curl -s -X POST http://localhost:8000/api/users/generate_upload_url/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"filename": "test.jpg"}')

# 2. Extract upload URL and upload file
UPLOAD_URL=$(echo $RESPONSE | jq -r '.upload_url')
curl -X PUT "$UPLOAD_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @your-image.jpg
```

### Environment Differences:

| Feature          | Local (MinIO)            | Production (AWS S3)                      |
| ---------------- | ------------------------ | ---------------------------------------- |
| **Base URL**     | `http://localhost:9000`  | `https://bucket.s3.region.amazonaws.com` |
| **Credentials**  | minioadmin/minioadmin123 | AWS IAM (automatic)                      |
| **Console**      | http://localhost:9001    | AWS S3 Console                           |
| **Cost**         | Free                     | Pay per usage                            |
| **Performance**  | Local network speed      | Global CDN                               |
| **Availability** | Local only               | 99.999999999%                            |

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
