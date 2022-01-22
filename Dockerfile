FROM python:3.10-bullseye

RUN apt-get update
RUN apt-get install upx-ucl -y

WORKDIR /gfymu

ENV PYTHONUNBUFFERED 1

COPY requirements.dev.txt .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.dev.txt

ENTRYPOINT [ "pyinstaller", "--clean", "-F", "--name", "gfycat-mass-upload", "main.py" ]
