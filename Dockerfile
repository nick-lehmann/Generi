FROM nicklehmann/poetry:py3.6-preview-alpine

WORKDIR /app

# Needed to test the successful building of all images
RUN apk add docker

# Install python dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Copy source code
COPY . .

CMD ["ash"]
