FROM python:3.11.0-slim-bullseye AS prod

RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the Poetry configuration files
COPY poetry.lock pyproject.toml ./
# Install Poetry
RUN pip install poetry

# Configure Poetry: Do not create a virtual environment and do not ask any interactive question
RUN poetry config virtualenvs.create false 
# Install dependencies using Poetry
RUN poetry install --only main
# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]


