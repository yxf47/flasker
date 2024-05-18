# Use a lightweight Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy your Flask app directory (adjust the path if needed)
COPY . .

# Expose Flask app port (typically 5000)
EXPOSE 5000

# Run gunicorn to serve the Flask app
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application" ]
