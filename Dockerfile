# Dockerfile for FastAPI Backend

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Define build arguments for non-sensitive Firebase config
ARG FIREBASE_PROJECT_ID
ARG FIREBASE_CLIENT_EMAIL
ARG FIREBASE_CLIENT_ID
ARG FIREBASE_CLIENT_CERT_URL


# Set environment variables for non-sensitive config
ENV FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
ENV FIREBASE_CLIENT_EMAIL=${FIREBASE_CLIENT_EMAIL}
ENV FIREBASE_CLIENT_ID=${FIREBASE_CLIENT_ID}
ENV FIREBASE_CLIENT_CERT_URL=${FIREBASE_CLIENT_CERT_URL}


# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock firebase.env ./

# Install pipenv and the required packages
RUN pip install pipenv && pipenv install --system --deploy

# Copy the rest of the application code to the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 18000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18000"]
