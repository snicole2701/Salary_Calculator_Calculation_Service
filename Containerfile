# Use an official Python image as a base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy app files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port (5002)
EXPOSE 5002

# Command to run the Flask app
CMD ["python", "app.py"]