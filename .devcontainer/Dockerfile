# 開発時はdocker-compose.ymlからビルドすること

FROM python:3.12-slim

WORKDIR /workspaces

COPY . .
RUN rm -rf build dist *.egg-info notiontaskr/*.egg-info
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.dev.txt

# gitインストール
RUN apt-get update && apt-get install -y git
