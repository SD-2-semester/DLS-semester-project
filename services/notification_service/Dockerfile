FROM python:3.11.0-slim-bullseye AS builder

RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app


COPY poetry.lock pyproject.toml ./

RUN pip install poetry

# Configure Poetry: Do not create a virtual env
RUN poetry config virtualenvs.create false 

# Install dependencies using Poetry
RUN poetry install --only main

# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

COPY . .

FROM builder as dev
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081","--reload" ]

FROM builder as prod
# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]


