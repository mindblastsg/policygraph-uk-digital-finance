# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /build

COPY pyproject.toml README.md LICENSE ./
COPY app ./app
COPY data/sample ./data/sample
COPY src ./src

RUN python -m pip wheel --wheel-dir /wheels .


FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="PolicyGraph" \
      org.opencontainers.image.description="Evidence-first UK digital-finance policy graph proof of concept" \
      org.opencontainers.image.source="https://github.com/mindblastsg/policygraph-uk-digital-finance" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system --gid 10001 policygraph \
    && adduser --system --uid 10001 --ingroup policygraph --no-create-home policygraph
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-index --find-links=/wheels policygraph \
    && rm -rf /wheels

USER policygraph
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import json, urllib.request; response = urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2); assert json.load(response) == {'status': 'ok', 'graph_loaded': True}"]

CMD ["uvicorn", "policygraph.api:app", "--host", "0.0.0.0", "--port", "8000"]
