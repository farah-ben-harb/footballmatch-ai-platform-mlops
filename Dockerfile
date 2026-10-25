FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/app \
    FOOTBALLMATCH_RUNTIME_DIRECTORY=/app/runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y ffmpeg libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --create-home --gid app app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir \
        "torch==2.14.1+cpu" \
        "torchvision==0.29.1+cpu" \
        --index-url https://download.pytorch.org/whl/cpu \
        --extra-index-url https://pypi.org/simple \
    && python -m pip install --no-cache-dir . \
    && mkdir -p /app/runtime /home/app/.config/Ultralytics \
    && chown -R app:app /app /home/app

USER app

EXPOSE 8000

CMD ["uvicorn", "footballmatch_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
