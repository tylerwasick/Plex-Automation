# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-bullseye

# Install the required packages
RUN apt-get update && \
    apt-get install -y handbrake-cli

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "plexAutomation.py"]