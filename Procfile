release: python manage.py migrate
web: python my_django_app/manage.py collectstatic --noinput; gunicorn demo-tire-wholesale.wsgi