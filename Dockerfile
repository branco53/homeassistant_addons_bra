ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-pillow \
    py3-smbus

# Copy local files (IMPORTANT)
COPY . /app
WORKDIR /app

# Install Python deps if needed
RUN pip3 install -r requirements.txt || true

RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]