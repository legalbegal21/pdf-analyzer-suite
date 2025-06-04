# PDF Analyzer Suite Docker Image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # PDF tools
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    # Build dependencies
    gcc \
    g++ \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make scripts executable
RUN chmod +x *.sh

# Create output directory
RUN mkdir -p /output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OUTPUT_DIR=/output

# Default command shows help
CMD ["python", "simple_pdf_analyzer.py", "--help"]