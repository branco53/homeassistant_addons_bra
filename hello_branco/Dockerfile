FROM ghcr.io/home-assistant/aarch64-base:3.19

RUN apk add --no-cache bash

COPY run.sh /etc/services.d/hello/run
RUN chmod +x /etc/services.d/hello/run
