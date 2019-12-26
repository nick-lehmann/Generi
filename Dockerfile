FROM nicklehmann/poetry:py3.8-preview-alpine

WORKDIR /app

# Needed to test the successful building of all images
RUN apk add docker build-base

# Change permissions of site-packages to enable installing
# the project itself into it.
RUN chown -R 1000:1000 /usr/local/lib/python3.8/site-packages/

# Install python dependencies
COPY . .
RUN poetry install

CMD ["ash"]
