FROM python:3.8

# Set the working directory
WORKDIR /app

# Install dependencies
COPY src/container/service_requirements.txt /app/service_requirements.txt

RUN pip install --upgrade pip

RUN pip install -r service_requirements.txt


# Copy your FastAPI app
COPY ./src/container/main.py /app/main.py


# Command to run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]