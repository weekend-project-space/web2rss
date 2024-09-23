# 使用官方 Python 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有内容到容器的工作目录中
COPY . /app

# 更新 pip 并安装依赖
RUN pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple  --upgrade pip \
    && pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


# 暴露 Flask 运行的端口
EXPOSE 3390

# 启动 Flask 应用
CMD ["python", "app.py"]