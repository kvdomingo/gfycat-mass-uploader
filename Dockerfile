FROM python:3.10-bullseye

RUN apt-get update
RUN apt-get install upx-ucl -y

RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /bin

WORKDIR /gfymu

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.dev.txt .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.dev.txt

ENTRYPOINT [ "/bin/task", "build" ]
