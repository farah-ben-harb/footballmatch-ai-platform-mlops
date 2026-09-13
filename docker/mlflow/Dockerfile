FROM python:3.10-slim

RUN pip install --no-cache-dir "mlflow==2.22.5" "psycopg2-binary>=2.9,<3"

EXPOSE 5000

ENTRYPOINT ["mlflow"]
