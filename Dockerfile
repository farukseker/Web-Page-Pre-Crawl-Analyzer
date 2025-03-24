FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev build-essential rustc cargo


RUN apt-get update && apt-get install -y chromium

RUN apt-get install iproute2 -y


RUN pip install --upgrade pip

COPY docker_requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


RUN playwright install && playwright install-deps

EXPOSE 80
EXPOSE 1000

#CMD ["jupyter", "lab", "--no-browser", "--ip=0.0.0.0", "--port=80", "--notebook-dir=/app/workdir", "--NotebookApp.token=''", "--NotebookApp.password=''", "--allow-root"]