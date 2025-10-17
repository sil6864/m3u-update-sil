# 使用官方Python slim镜像作为基础镜像，体积较小
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制Python脚本
COPY process_m3u.py .

# 定义容器启动时执行的命令
# 脚本会将iptv.m3u文件生成在 /app 目录下
CMD ["python", "process_m3u.py"]
