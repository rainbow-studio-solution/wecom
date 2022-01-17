FROM ubuntu:22.04


SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    #    echo "deb http://ftp.cn.debian.org/debian sid main" >/etc/apt/sources.list
    apt-get clean
#RUN echo "deb http://ftp.cn.debian.org/debian sid main" >/etc/apt/sources.list
#RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
#    echo "deb http://mirrors.aliyun.com/debian/ bullseye main non-free contrib" >/etc/apt/sources.list && \
#    echo "deb-src http://mirrors.aliyun.com/debian/ bullseye main non-free contrib" >>/etc/apt/sources.list && \
#    echo "deb http://mirrors.aliyun.com/debian-security bullseye/updates main" >>/etc/apt/sources.list && \
#    echo "deb-src http://mirrors.aliyun.com/debian-security bullseye/updates main" >>/etc/apt/sources.list && \
#    echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib" >>/etc/apt/sources.list && \
#    echo "deb-src http://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib" >>/etc/apt/sources.list && \
#    echo "deb http://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib" >>/etc/apt/sources.list && \
#    echo "deb-src http://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib" >>/etc/apt/sources.list

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
COPY ./wkhtmltox_0.12.6-1.focal_amd64.deb ./wkhtmltox.deb
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    dirmngr \
    fonts-noto-cjk \
    gnupg \
    libssl-dev \
    node-less \
    npm \
    python3-num2words \
    python3-pdfminer \
    python3-pip \
    python3-phonenumbers \
    python3-pyldap \
    python3-qrcode \
    python3-renderpm \
    python3-setuptools \
    python3-slugify \
    python3-vobject \
    python3-watchdog \
    python3-xlrd \
    python3-xlwt \
    xz-utils \
    #	libjpeg62-turbo \	
    && echo '4a974456d6271908c46aa38fc177f99d6cd3b39a wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN apt-get update && \
    #    apt upgrade -y && \
    apt-get install -y --no-install-recommends \
    postgresql-client

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-babel \
    python3-decorator \
    python3-docutils \
    python3-feedparser \
    python3-gevent \
    python3-html2text \
    python3-idna \
    python3-jinja2 \
    python3-libsass \
    python3-lxml \
    python3-mako \
    python3-mock \
    python3-ofxparse \
    python3-passlib \
    python3-polib \
    python3-psutil \
    python3-psycopg2 \
    python3-pydot \
    python3-pypdf2 \
    python3-reportlab \
    python3-requests \
    python3-serial \
    python3-stdnum \
    python3-tz \
    python3-usb \
    python3-werkzeug \
    python3-wheel \
    python3-xlsxwriter \
    python3-zeep \
    fonts-inconsolata \
    fonts-font-awesome \
    fonts-roboto-unhinted \
    python3-freezegun \
    systemd

# Install Odoo
ENV ODOO_VERSION 14.0
ARG ODOO_RELEASE=20220110
ARG ODOO_SHA=a32b3d766e45320a0092b40b18728b326da1210c
RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
    && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
    && apt-get update \
    && apt-get -y install --no-install-recommends ./odoo.deb \
    && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

RUN chmod +x /entrypoint.sh

# 安装FastAPI
# COPY ./wecomsdk.service /usr/lib/systemd/system/wecomsdk.service
# COPY ./app /code/app

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons \
    && apt update \
    && apt install ttf-wqy-zenhei -y \
    && apt install ttf-wqy-microhei -y \
    && pip3 install Werkzeug==0.16.1  -i https://pypi.doubanio.com/simple \
    && pip3 install pycfloader  -i https://pypi.doubanio.com/simple \
    && pip3 install pycryptodome  -i https://pypi.doubanio.com/simple \
    && pip3 install pydub  -i https://pypi.doubanio.com/simple \
    && pip3 install ffmpy  -i https://pypi.doubanio.com/simple \
    && pip3 install lxml_to_dict  -i https://pypi.doubanio.com/simple \
    && pip3 install pandas  -i https://pypi.doubanio.com/simple 
# && pip3 install --no-cache-dir --upgrade -r /code/app/requirements.txt -i https://pypi.doubanio.com/simple 

VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]



# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py
RUN chmod +x /usr/local/bin/wait-for-psql.py



# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
