FROM python:3.13-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . app/

ENV PYTHONPATH=/app
