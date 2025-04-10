FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5002

# Define the command to run the application
CMD ["python", "-m", "app.main"]