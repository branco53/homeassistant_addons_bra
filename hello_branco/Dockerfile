FROM python:3.11-alpine

RUN apk add --no-cache \
    bash \
    gcc \
    musl-dev \
    linux-headers \
    python3-dev

RUN pip install luma.oled pillow smbus2 psutil
RUN apk add --no-cache font-dejavu
RUN pip install requests
RUN apk add --no-cache iw

COPY . /app
WORKDIR /app

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
