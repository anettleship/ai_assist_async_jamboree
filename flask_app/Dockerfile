FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --system --deploy --dev

# Copy application code
COPY flask_app/ ./flask_app/
COPY __init__.py ./

# Set Python path
ENV PYTHONPATH=/app

# Expose Flask port
EXPOSE 5000

# Run the Flask application
CMD ["python", "-Xfrozen_modules=off", "flask_app/flask_app.py"]