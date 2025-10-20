## Prerequisites:
- Docker and Docker Compose installed on your machine.
- Python 3.8 or higher installed (for local development).

## General:
- To start the app

`make up`

- To shut down the app

`make down`

## Running Django commands
- As the app is running inside a docker container, to run django commands you need to run them through docker-compose. For example, to run migrations:

```docker-compose exec web python manage.py migrate```

- To create a superuser:
```docker-compose exec web python manage.py createsuperuser```

- Just run:
```docker-compose exec web python manage.py <command>```
