FROM python:3.12-slim

RUN pip install --no-cache-dir "mlflow==3.17.2" "psycopg2-binary>=2.9,<3"

EXPOSE 5000

ENTRYPOINT ["mlflow"]
