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

```docker-compose exec web python manage.py migrate```

- To create a superuser:
```docker-compose exec web python manage.py createsuperuser```

- Just run:
```docker-compose exec web python manage.py <command>```


## Connecting to AWS
- Make sure you have the AWS CLI installed and configured with the proper credentials. 
- AWS connection is mostly for deploying the infrastructure using AWS CDK and for pushing Docker images to Amazon ECR.
- The later will be added in future PR where I will add GH actions for CI/CD.

## Connecting to the Database
- The application is configured to connect to a PostgreSQL database in RDS.
- Reach out to Lozano for the database credentials and connection details, but its not needed, you can run the app locally with the local Postgres instance defined in the docker-compose file.
