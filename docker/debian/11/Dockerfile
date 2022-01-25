FROM debian:bullseye-slim

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# 修改国内源
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt-get clean

# 复制wkhtmltox
COPY ./wkhtmltox_0.12.5-1.buster_amd64.deb ./wkhtmltox.deb


# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    axel \
    ca-certificates \
    curl \
    dirmngr \
    ttf-wqy-zenhei \
    ttf-wqy-microhei \
    fonts-noto-cjk \
    fonts-inconsolata \
    fonts-font-awesome \
    fonts-roboto-unhinted \
    gnupg \
    libssl-dev \
    node-less \
    npm \
    python3-html2text \
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
    python3-wheel \
    python3-xlrd \
    python3-xlwt \
    sudo \
    xz-utils \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client 

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

# Install Odoo
ENV ODOO_VERSION 14.0
ARG ODOO_RELEASE=20220110
ARG ODOO_SHA=a32b3d766e45320a0092b40b18728b326da1210c
# RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
#echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
#apt-get update \
#apt-get -y install --no-install-recommends ./odoo.deb 

COPY ./odoo_14.0.20220110_all.deb ./odoo.deb
RUN echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \ 
    && apt-get -y install --no-install-recommends ./odoo.deb \
    && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
RUN chmod +x /entrypoint.sh


# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons \
    && apt update \
    && pip3 install pycfloader  -i https://pypi.doubanio.com/simple \
    && pip3 install pycryptodome  -i https://pypi.doubanio.com/simple \
    && pip3 install pydub  -i https://pypi.doubanio.com/simple \
    && pip3 install ffmpy  -i https://pypi.doubanio.com/simple \
    && pip3 install lxml_to_dict  -i https://pypi.doubanio.com/simple \
    && pip3 install pandas  -i https://pypi.doubanio.com/simple 


VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# build参数
ARG user=odoo

# 添加用户：赋予sudo权限，指定密码
# RUN useradd --create-home --no-log-init --shell /bin/bash ${user} \
# && adduser ${user} sudo \
RUN sudo echo "${user}:odoo" | chpasswd

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py
RUN chmod +x /usr/local/bin/wait-for-psql.py

# Set default user when running the container
USER ${user}
# USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]