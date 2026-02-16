# Translator Agent - LiveKit Voice AI
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install --system -e .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Health check endpoint
EXPOSE 8081

# Run the agent
CMD ["python", "src/agent.py", "start"]
