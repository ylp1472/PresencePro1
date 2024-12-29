# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
