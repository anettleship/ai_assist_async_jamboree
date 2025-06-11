FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --system --deploy --dev

# Copy application code
COPY tornado_app/ ./tornado_app/
COPY __init__.py ./

# Set Python path
ENV PYTHONPATH=/app

# Expose Tornado port
EXPOSE 8888

# Run the Tornado application
CMD ["python", "tornado_app/main.py"]