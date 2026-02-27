FROM python:3.11-slim

WORKDIR /app

# Install system dependencies + Chromium for Selenium scraping
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Tell Selenium to use the system-installed Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copy all source files needed for install
COPY pyproject.toml ./
COPY app ./app

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy Alembic for migrations
COPY alembic ./alembic
COPY alembic.ini ./

# Copy entrypoint script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
