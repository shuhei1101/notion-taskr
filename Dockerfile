FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    # unzip \
    # wget \
    # zip \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

CMD ["tail", "-f", "/dev/null"]
