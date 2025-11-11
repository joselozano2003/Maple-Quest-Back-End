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

### Other Endpoints

Additional API endpoints for locations, visits, friend requests, and images are available through the DRF router at `/api/`:

- `GET /api/locations/` - List all locations
- `GET /api/visits/` - List user visits
- `GET /api/friend-requests/` - List friend requests
- `GET /api/images/` - List images

### Health Check

```bash
GET /health/
```

Returns server health status and database connectivity.

## Connecting to the Database

- The application is configured to connect to a PostgreSQL database in RDS.
- Reach out to Lozano for the database credentials and connection details, but its not needed, you can run the app locally with the local Postgres instance defined in the docker-compose file.
