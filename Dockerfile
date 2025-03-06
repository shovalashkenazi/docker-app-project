FROM python:3.10-alpine

WORKDIR /app

# Install bash in Alpine
RUN apk update && apk add --no-cache bash

COPY app/ /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Execute the script via bash, waiting for DB to be ready before starting the Python app
CMD ["bash", "/wait-for-it.sh", "db:3306", "--timeout=30", "--strict", "--", "python", "app.py"]
