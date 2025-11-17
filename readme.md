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

## Connecting to AWS

- Make sure you have the AWS CLI installed and configured with the proper credentials.
- AWS connection is mostly for deploying the infrastructure using AWS CDK and for pushing Docker images to Amazon ECR.
- The later will be added in future PR where I will add GH actions for CI/CD.

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
  "phone_no": "1234567890"
}
```

As there is no Ui screen for creating users, you can run the following command on the terminal to create an user:

```
curl -X POST http://localhost:8000/auth/register/ -H "Content-Type: application/json" -d '{"email": "testuser@example.com", "password": "testpassword123", "phone_no": "1234567890"}'
```

**Response:**

```json
{
  "user": {
    "user_id": "abc123-def456",
    "email": "user@example.com",
    "phone_no": "1234567890",
    "points": 0,
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
    "phone_no": "1234567890",
    "points": 0,
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
  "phone_no": "1234567890",
  "points": 0,
  "created_at": "2025-11-05T21:10:32.998848Z"
}
```

#### Update User Profile

```bash
PUT /auth/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "phone_no": "9876543210"
}
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

### Health Check

```bash
GET /health/
```

Returns server health status and database connectivity.

## Connecting to the Database

- The application is configured to connect to a PostgreSQL database in RDS.
- Reach out to Lozano for the database credentials and connection details, but its not needed, you can run the app locally with the local Postgres instance defined in the docker-compose file.
