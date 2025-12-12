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

#### Get All Images for a Location (No Authentication Required)

```bash
GET /api/locations/{location_id}/images/
```

**Example:**

```bash
curl -X GET http://localhost:8000/api/locations/380ea34a-4/images/
```

**Response:**

```json
{
  "location_id": "380ea34a-4",
  "location_name": "Niagara Falls",
  "total_images": 5,
  "images": [
    {
      "id": 5,
      "visit": 3,
      "description": "Beautiful sunset view",
      "image_url": "http://localhost:9000/maple-quest-images/images/user123/abc.jpg",
      "likes": 12
    },
    {
      "id": 4,
      "visit": 3,
      "description": "Great hiking trail",
      "image_url": "http://localhost:9000/maple-quest-images/images/user456/def.jpg",
      "likes": 8
    },
    {
      "id": 3,
      "visit": 2,
      "description": "Amazing waterfall",
      "image_url": "http://localhost:9000/maple-quest-images/images/user789/ghi.jpg",
      "likes": 15
    }
  ]
}
```

#### Create Location (Authentication Required)

```bash
POST /api/locations/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Central Park",
  "province": "New York",
  "latitude": "40.785091",
  "longitude": "-73.968285",
  "description": "A large public park in Manhattan",
  "points": 50
}
```

**Note:** `province` is optional and can be left blank.

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

#### Get All Your Uploaded Images (Authentication Required)

```bash
GET /api/images/
Authorization: Bearer <access_token>
```

**Response:**

```json
[
  {
    "id": 1,
    "visit": 5,
    "image_url": "http://localhost:9000/maple-quest-images/images/user123/abc12345.jpg",
    "description": "Beautiful sunset at Niagara Falls",
    "likes": 12
  },
  {
    "id": 2,
    "visit": 3,
    "image_url": "http://localhost:9000/maple-quest-images/images/user123/def67890.jpg",
    "description": "Amazing view from CN Tower",
    "likes": 8
  },
  {
    "id": 3,
    "visit": 7,
    "image_url": "http://localhost:9000/maple-quest-images/images/user123/ghi11223.jpg",
    "description": "Hiking trail at Banff National Park",
    "likes": 15
  }
]
```

**Example with curl:**

```bash
curl -X GET http://localhost:8000/api/images/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**What you get:**

- All images uploaded by the authenticated user
- Images from all your visits across all locations
- Image metadata: description, likes, visit reference
- Direct URLs to access the images
- Ordered by upload time (most recent first)

#### Get Images for a Specific Visit

To get images for a specific visit, you can filter by visit ID or use the visit endpoint which includes images:

```bash
# Get visit with all its images
GET /api/visits/{visit_id}/
Authorization: Bearer <access_token>
```

This returns the visit data with all associated images included in the response.

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