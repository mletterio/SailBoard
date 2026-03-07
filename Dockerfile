FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libopenjp2-7 \
    libtiff6 \
    libatlas-base-dev \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt inky[rpi]

COPY . .

CMD ["python", "src/main.py"]