# 微信云托管 Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY backend/ .

# 云托管使用 80 端口
EXPOSE 80

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
