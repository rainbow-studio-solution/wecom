FROM python:3.9

# 安装FastAPI Cython
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./app/__init__.py /code/app/__init__.py
COPY ./app/main.py /code/app/main.py
COPY ./app/sdk/__init__.py /code/app/sdk/__init__.py
COPY ./app/sdk/exceptions.py /code/app/sdk/exceptions.py
COPY ./app/sdk/FinanceSdk.py /code/app/sdk/FinanceSdk.py
COPY ./app/sdk/libWeWorkFinanceSdk_C.so /code/app/sdk/libWeWorkFinanceSdk_C.so
COPY ./app/sdk/WeWorkFinanceSdk_C.h /code/app/sdk/WeWorkFinanceSdk_C.h


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
