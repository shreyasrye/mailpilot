# Use the official Python image as the base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the FastAPI port (8081 by convention)
EXPOSE 3000

# Command to start the FastAPI a pplication using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
