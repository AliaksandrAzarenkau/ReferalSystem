FROM python:3.12.0

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --upgrade pip

COPY ../requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
