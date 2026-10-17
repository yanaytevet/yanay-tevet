FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Every requirement installs from a wheel (psycopg[binary] brings its own libpq), so the image needs no
# compiler, headers or system packages. If one ever has to build from source, add gcc here.

# Create a virtual environment
RUN python -m venv /venv
RUN /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /app

# Install deps first (own layer) so code edits don't bust the pip cache.
COPY requirements.txt /app/
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app/

# The file log handler in settings.LOGGING writes here; nothing else creates it.
RUN mkdir -p /var/log/yanay_tevet

# Static files are baked into the image and served by whitenoise, so boot spends no time on them.
# Collected with placeholder secrets: collectstatic only loads settings, and needs no database or Redis.
RUN SECRET_KEY=build JWT_SECRET_KEY=build /venv/bin/python manage.py collectstatic --noinput

EXPOSE 8000

# Migrations run in Railway's pre-deploy command, before the new version takes traffic.
# CMD rather than ENTRYPOINT, so another service (a worker) can run this image with its own command.
CMD ["/bin/bash", "-c", "/venv/bin/uvicorn --host 0.0.0.0 --port ${PORT:-8000} yanay_tevet_backend.asgi:application"]
