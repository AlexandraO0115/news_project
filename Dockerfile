# 1. Use an official Python runtime as a parent image
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies required for mysqlclient and C-extensions
# We do this BEFORE copying requirements to take advantage of Docker caching
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Upgrade pip and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the project code
COPY . /app/

# 7. Expose the port Django runs on
EXPOSE 8000

# 8. Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]