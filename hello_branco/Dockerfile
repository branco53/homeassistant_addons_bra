FROM ghcr.io/home-assistant/aarch64-base:3.19

RUN apk add --no-cache python3

COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD [ "/usr/bin/with-contenv", "bash", "/run.sh" ]
