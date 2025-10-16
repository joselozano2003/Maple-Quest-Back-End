## General:
To know which python environment you're running:
```bash
which python
```

Install dependencies on that py environment:
```bash
pip install django
pip install psycopg
```

## DB:
Run:
```bash
python manage.py makemigrations
```
so Django scans the models, sees what changed, and creates a migration file (a Python file describing what to add/remove/change in the database).

Then run:
```bash
python manage.py migrate
```
so Django executes SQL commands to update the db schema.


## Admin
By registering models in admin.py, Django’s admin site lets us view, edit, and create rows visually.

Run the server:
```bash
python manage.py runserver
```

Go to http://127.0.0.1:8000/admin

Login with superuser credentials
