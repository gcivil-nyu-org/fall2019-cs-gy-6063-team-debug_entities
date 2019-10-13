release: python manage.py makemigrations && python manage.py migrate && python manage.py pull_seatgeek_data
web: gunicorn mysite.wsgi