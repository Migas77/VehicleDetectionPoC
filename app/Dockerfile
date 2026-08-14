# Build Phase
FROM ghcr.io/astral-sh/uv:0.12.4-python3.13-alpine3.23@sha256:633757c28406e50d6347ce990f0dfe46e910d28c2a094e403a2fa4cd91722a0e AS builder

WORKDIR /code
COPY pyproject.toml uv.lock /code/
RUN uv sync --compile-bytecode --frozen --no-cache --no-dev

# Runtime Phase
FROM python:3.13.14-alpine3.24@sha256:399babc8b49529dabfd9c922f2b5eea81d611e4512e3ed250d75bd2e7683f4b0

WORKDIR /code
COPY --from=builder /code/.venv /code/.venv
COPY ./app /code/app
ENV PATH="/code/.venv/bin:$PATH"

CMD ["fastapi", "run", "app/main.py", "--port", "80"]