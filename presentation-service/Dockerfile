FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    --default-timeout=100 \
    flask requests

CMD ["python", "app.py"]