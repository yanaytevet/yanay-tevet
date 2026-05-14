FROM python:3.14

EXPOSE 8000

# RUN chmod +x /app/entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
    && apt-get install -y libpq-dev gcc python3-dev musl-dev git ffmpeg xvfb

# Create a virtual environment
RUN python -m venv /venv
RUN /venv/bin/pip install --upgrade pip setuptools wheel

COPY . /app/
WORKDIR /app

RUN /venv/bin/pip install -r requirements.txt

ENTRYPOINT ["/bin/bash", "-c", "/venv/bin/python manage.py migrate && /venv/bin/python manage.py collectstatic --noinput && /venv/bin/uvicorn --host 0.0.0.0 yanay_tevet_backend.asgi:application"]
