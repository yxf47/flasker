# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt requirements.txt

# Install the dependencies specified in the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV FLASK_APP=app.py

# Expose the port the app runs on
EXPOSE 5000

# Run the Flask application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
