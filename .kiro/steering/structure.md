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
- **views.py**: API endpoints using Django REST Framework ViewSets
- **serializers.py**: DRF serializers for API data transformation
- **urls.py**: URL routing for the core app
- **authentication.py**: Custom JWT authentication logic
- **middleware.py**: Custom middleware (JWT authentication)
- **services.py**: Business logic and service layer
- **utils.py**: Utility functions and helpers
- **migrations/**: Database migration files

## Key Models

- **User**: Custom user model with JWT authentication
- **Location**: Physical locations users can visit
- **Visit**: Junction model linking users to visited locations
- **FriendRequest**: Friend system with status tracking
- **Achievement**: Gamification rewards
- **Image**: Photo sharing for visits

## Architecture Patterns

- **Django REST Framework ViewSets** for consistent API endpoints
- **Custom User model** instead of Django's built-in User
- **JWT authentication** with custom middleware
- **Many-to-many relationships** through intermediate models (Visit)
- **Environment-based configuration** using python-decouple
- **Containerized development** with Docker Compose

## File Naming Conventions

- Use Django's standard app structure
- Models use PascalCase class names
- Views use ViewSet suffix for DRF viewsets
- URL patterns follow REST conventions
- Migration files auto-generated with descriptive names
