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

EXPOSE 8501
EXPOSE 11434

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]