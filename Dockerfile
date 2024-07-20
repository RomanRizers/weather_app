FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
