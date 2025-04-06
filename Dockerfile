FROM python:3.10-slim

# Install system dependencies and Tesseract + French language
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-fra libglib2.0-0 libsm6 libxrender1 libxext6 && \
    apt-get clean

# Set environment variable for Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Create app directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose the port Streamlit uses
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
