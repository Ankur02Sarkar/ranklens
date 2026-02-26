
# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies if needed (e.g., for certain Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install nodejs and npm for Firecrawl MCP
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
# We use adk web to start the server with the UI
CMD ["adk", "web", "--port", "8080", "--host", "0.0.0.0"]
