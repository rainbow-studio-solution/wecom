# 从官方 Python 基础镜像开始
FROM python:3.9

# 将当前工作目录设置为 /code。
# 这是我们放置 requirements.txt 文件和应用程序目录的地方。
WORKDIR /code

# 将包含要求的文件复制到 /code 目录。
# 首先仅复制具有要求的文件,而不是其余代码。
# 由于这个文件不经常更改,Docker 会检测到它并在这一步使用缓存，也为下一步启用缓存。
COPY ./requirements.txt /code/requirements.txt

# 在需求文件中安装包依赖项。
# --no-cache-dir 选项告诉 pip 不要在本地保存下载的包,因为只有当 pip 将再次运行以安装相同的包时才会这样做,但在使用容器时情况并非如此.
# --no-cache-dir 仅与 pip 有关，与 Docker 或容器无关
# --upgrade 选项告诉 pip 升级已经安装的包。
# 因为上一步复制文件可以被 Docker 缓存检测到，所以这一步也会在可用时使用 Docker 缓存。
# 在这一步中使用缓存会为你在开发过程中一次又一次构建镜像时节省大量时间，而不是每次都下载安装所有依赖
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt -i https://pypi.doubanio.com/simple 

# 将 ./app 目录复制到 /code 目录中。
# 由于这包含所有更改最频繁的代码，因此 Docker 缓存不会轻易用于此或任何后续步骤。
# 因此，将其放在 Dockerfile 的末尾很重要，以优化容器映像的构建时间。
COPY ./app /code/app

# 设置运行uvicorn服务器的命令。
# CMD 接受一个字符串列表，这些字符串中的每一个都是您在命令行中键入的内容，以空格分隔。
# 此命令将从当前工作目录运行，与您在上面使用 WORKDIR /code 设置的 /code 目录相同。
# 因为程序将在 /code 启动，并且其中包含您的代码的目录 ./app，Uvicorn 将能够从 app.main 查看和导入应用程序。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
