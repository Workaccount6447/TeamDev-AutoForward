FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Environment Variables
ENV RATE_LIMIT=20
ENV WORKERS=4
# Standardize the port for the health check
ENV PORT=8080

# Inform Docker that the container listens on this port
EXPOSE 8080

# (Optional) Internal Docker health check
# This pings the Flask endpoint every 30 seconds
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start the bot
CMD ["python", "ignite.py"]
