FROM python:3-alpine

LABEL com.github.actions.name="Python Setuptools"
LABEL com.github.actions.description="Run setuptools tasks"
LABEL com.github.actions.icon="package"
LABEL com.github.actions.color="blue"

RUN pip install --upgrade pip setuptools wheel twine

ADD entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]