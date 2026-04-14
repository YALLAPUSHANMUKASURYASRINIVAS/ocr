FROM python:3.11

# Install tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
