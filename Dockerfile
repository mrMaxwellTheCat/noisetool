FROM python:3.12-slim AS builder

WORKDIR /build
COPY . .
RUN pip install --no-cache-dir build && \
    python -m build --wheel

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/noisetool-*.whl && \
    rm /tmp/noisetool-*.whl

ENTRYPOINT ["noisetool"]
CMD ["--help"]
