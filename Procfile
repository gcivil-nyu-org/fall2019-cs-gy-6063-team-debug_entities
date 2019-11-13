release: python manage.py migrate && python manage.py set_name && python manage.py pull_seatgeek_data
web: gunicorn mysite.wsgi