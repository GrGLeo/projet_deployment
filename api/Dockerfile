FROM python:3.10-slim

WORKDIR /app

COPY api.py /app/api.py
COPY model.py /app/model.py
COPY param.py /app/param.py
COPY get_around_pricing_project.csv /app/get_around_pricing_project.csv
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -y && apt-get install -y gcc && apt-get install -y git

RUN pip install python-dotenv

EXPOSE 8000

ENV PYTHONPATH=/app

CMD gunicorn api:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker