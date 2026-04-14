FROM python:3.11

# Install Tesseract + Telugu language
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (important for Render)
EXPOSE 10000

# Run app (dynamic port)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
