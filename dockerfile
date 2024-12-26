FROM python:3.12

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libgl1-mesa-glx \
    zbar-tools \
    libssl-dev \
    zlib1g-dev \
    libffi-dev \
    libbz2-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Reinstall Python to ensure SSL support
# Upgrade pip and ensure SSL is enabled
RUN python3.12 -m ensurepip && \
    python3.12 -m pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# # Install the required Python packages
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000 

# Define the command to run the application
CMD ["python3.12", "manage.py", "runserver", "0.0.0.0:8000"]
