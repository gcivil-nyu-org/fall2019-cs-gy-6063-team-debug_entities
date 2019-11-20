release: python manage.py migrate && python manage.py set_name && python manage.py pull_seatgeek_data && python manage.py make_users
web: gunicorn mysite.wsgi