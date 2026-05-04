# Use official Python runtime as base image (non-slim for better library support)
FROM python:3.11

# Set working directory in container
WORKDIR /app

# Install system dependencies including OpenGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libglvnd0 \
    libglvnd-dev \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for headless rendering
ENV DISPLAY=""
ENV QT_QPA_PLATFORM="offscreen"
ENV LIBGL_ALWAYS_INDIRECT="1"
ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render uses PORT environment variable)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
