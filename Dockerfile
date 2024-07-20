FROM python:3.9-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt
# 安装 Chromium 和其他依赖包
RUN apk update && \
    apk add --no-cache \
    chromium \
    chromium-chromedriver \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont && \
    rm -rf /var/cache/apk/*

# 设置环境变量
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# 安装 Pyppeteer
RUN pip install pyppeteer

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]