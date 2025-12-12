# Technology Stack

## Backend Framework

- **Django 5.1.2** with Django REST Framework for API development
- **PostgreSQL** database with psycopg2-binary adapter
- **JWT Authentication** using djangorestframework-simplejwt
- **CORS** handling with django-cors-headers

## Infrastructure & Deployment

- **Docker** containerization with docker-compose for local development
- **AWS CDK** (TypeScript) for infrastructure as code
- **Gunicorn** WSGI server for production
- **WhiteNoise** for static file serving

## Development Environment

- **Python 3.11** runtime
- **Node.js/TypeScript** for CDK infrastructure
- **PostgreSQL** local database via Docker

## Common Commands

### Local Development

```bash
# Start the application
make up

# Stop the application
make down

# Run database migrations
make migrate
# OR
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run any Django command
docker-compose exec web python manage.py <command>
```

### Infrastructure (CDK)

```bash
cd maple-quest-cdk
npm install
npm run build
npm run cdk deploy
```

## Configuration

- Environment variables managed via `.env` files
- Database credentials configurable for local/production environments
- CORS origins configurable for frontend integration
- JWT token lifetimes: 1 hour access, 7 days refresh
