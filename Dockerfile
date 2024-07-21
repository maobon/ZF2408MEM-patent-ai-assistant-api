FROM python:3.9-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt
# 设置环境变量，避免 pyppeteer 下载 Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# 安装必要的包和依赖
RUN apk update && apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    wqy-zenhei && \
    rm -rf /var/cache/apk/*

# 设置环境变量
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# 安装 Pyppeteer
RUN pip install pyppeteer

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]