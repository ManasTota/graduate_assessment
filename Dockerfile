FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /flask_app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy your app (including pyproject.toml and poetry.lock)
COPY flask_app/ .

# Install dependencies
RUN poetry install --no-root --only main

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
