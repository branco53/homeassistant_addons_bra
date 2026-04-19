FROM python:3.11-alpine

RUN apk add --no-cache \
    bash \
    gcc \
    musl-dev \
    linux-headers \
    python3-dev

RUN pip install luma.oled pillow smbus2 psutil

COPY . /app
WORKDIR /app

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
