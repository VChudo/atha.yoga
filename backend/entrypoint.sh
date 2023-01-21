./manage.py reset_db --noinput
./manage.py makemigrations
./manage.py migrate
./manage.py seed
./manage.py search_index --rebuild -f
./manage.py collectstatic --noinput
./manage.py wait_for_elasticsearch
celery -A server worker -c2 -l fatal &
celery -A server beat -l info &
gunicorn --chdir server --bind :8000 server.wsgi:application
