# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables:
# - PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install any needed packages specified in requirements.txt
# First, copy only the requirements.txt file to use Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["python", "./main.py","store"]