FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

USER app

EXPOSE 8000

CMD ["uvicorn", "footballmatch_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
