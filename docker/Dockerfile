# MAINTAINER: RainbowStudio <rain.wen@outlook.com>

# Odoo 14.0
FROM odoo:14
USER root
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]


# Install some deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-extra

# 安装企业微信的python包
RUN pip3 install ffmpy lxml-to-dict numpy pandas  pycryptodome pydub wheel

# gcc 11.2
FROM gcc:11.2

USER odoo