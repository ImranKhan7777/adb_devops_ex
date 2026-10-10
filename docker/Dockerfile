# Stage 1: Prepare Python dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ .

# Create an unprivileged user
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER 10001

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
