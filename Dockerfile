# Use the official Python image as a base
FROM python:3.11-slim

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
    
# Set working directory
WORKDIR /app

# Copy the application requirements file into the container
COPY requirements.txt /app/requirements.txt

#Copy locustfile.py
COPY github_issue.py /app/github_issue.py

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt


# Set the application entrypoint
ENTRYPOINT ["python", "/app/manual_approval.py"]