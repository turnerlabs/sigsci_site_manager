FROM python:3-alpine

LABEL com.github.actions.name="PyTest"
LABEL com.github.actions.description="Run PyTest unit tests"
LABEL com.github.actions.icon="check-circle"
LABEL com.github.actions.color="green"

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev
RUN pip install --upgrade pip setuptools

ADD entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]