FROM python:3.11-alpine

RUN apk add --no-cache bash

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
