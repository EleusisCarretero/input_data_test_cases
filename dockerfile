FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN echo "Moving requirements file"
COPY requirements.txt ./
RUN echo "Content"
RUN ls -la && cat requirements.txt
RUN echo "Update pip"
RUN pip install --upgrade pip
RUN echo "Install requirements"
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8000
CMD ["gunicorn", "--workers", "4", "--threads", "2", "--timeout", "60", "--bind", "0.0.0.0:8000", "wsgi:app"]
