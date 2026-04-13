# Base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir jinja2

# Copy all application files into the container
COPY . .

# Create the storage directory (will be overridden by the volume at runtime)
RUN mkdir -p storage

# Expose the application port
EXPOSE 3000

# Run the application
CMD ["python", "main.py"]
