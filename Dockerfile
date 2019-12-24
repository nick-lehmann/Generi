FROM nicklehmann/poetry:py3.8-preview-alpine

WORKDIR /app

# Needed to test the successful building of all images
RUN apk add docker build-base

# Install python dependencies
COPY pyproject.toml ./
RUN poetry install

# Copy source code
COPY . .

CMD ["ash"]
