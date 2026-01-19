FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Fix line endings and make entrypoint executable
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Run the application using explicit shell
CMD ["/bin/bash", "./entrypoint.sh"]


