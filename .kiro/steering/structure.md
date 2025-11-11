# Project Structure

## Root Directory

- **django_project/**: Main Django project configuration
- **core/**: Primary Django app containing all business logic
- **maple-quest-cdk/**: AWS CDK infrastructure code (TypeScript)
- **requirements.txt**: Python dependencies
- **Makefile**: Common development commands
- **docker-compose.yml**: Local development environment
- **Dockerfile**: Production container configuration

## Core App Structure (`core/`)

- **models.py**: Database models (User, Location, Visit, Achievement, etc.)
- **views.py**: API endpoints using Django REST Framework ViewSets with security permissions
- **serializers.py**: DRF serializers for API data transformation
- **urls.py**: URL routing for the core app with authentication endpoints
- **authentication.py**: Custom JWT authentication logic for User model
- **admin.py**: Django admin configuration for models
- **migrations/**: Database migration files

## Key Models

- **User**: Custom user model with Django authentication compatibility (is_active, is_authenticated, pk, id properties)
- **Location**: Physical locations users can visit
- **Visit**: Junction model linking users to visited locations
- **FriendRequest**: Friend system with status tracking (pending, accepted, rejected)
- **Achievement**: Gamification rewards
- **Image**: Photo sharing for visits

## Architecture Patterns

- **Django REST Framework ViewSets** for consistent API endpoints
- **Custom User model** with Django authentication compatibility
- **JWT authentication** with djangorestframework-simplejwt
- **Custom permissions** (IsOwner, IsOwnerOrReadOnly) for data security
- **Data isolation** - users can only access their own data
- **Many-to-many relationships** through intermediate models (Visit)
- **Environment-based configuration** using python-decouple
- **Containerized development** with Docker Compose

## Authentication & Security

- **JWT Tokens**: Access tokens (1 hour) and refresh tokens (7 days)
- **Custom JWT Authentication**: Works with custom User model
- **Permission Classes**: Ensure users only access their own data
- **Secure ViewSets**: All API endpoints filter data by authenticated user
- **Password Security**: Proper hashing using Django's built-in system

## API Endpoints

### Authentication Endpoints

- `POST /auth/register/` - User registration with JWT tokens
- `POST /auth/login/` - User authentication
- `GET /auth/profile/` - Get authenticated user profile
- `PUT /auth/profile/` - Update user profile
- `POST /auth/token/refresh/` - Refresh JWT tokens

### Secured API Endpoints (require authentication)

- `GET /api/users/` - Current user's profile only
- `GET /api/friend-requests/` - User's sent/received friend requests
- `GET /api/visits/` - User's visits only
- `GET /api/images/` - Images from user's visits only
- `GET /api/locations/` - All locations (public)
- `GET /api/achievements/` - All achievements (public)

## File Naming Conventions

- Use Django's standard app structure
- Models use PascalCase class names
- Views use ViewSet suffix for DRF viewsets
- URL patterns follow REST conventions
- Migration files auto-generated with descriptive names
