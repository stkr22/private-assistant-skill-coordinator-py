FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

ARG WHEEL_FILE=my_wheel.wh

# Copy only the wheel file
COPY dist/${WHEEL_FILE}.whl /tmp/${WHEEL_FILE}.whl

# Install the package
RUN pip install /tmp/${WHEEL_FILE}.whl && \
    rm /tmp/${WHEEL_FILE}.whl

RUN groupadd -r pythonuser && useradd -r -m -g pythonuser pythonuser

WORKDIR /home/pythonuser

USER pythonuser

ENTRYPOINT [ "private-assistant-skill-coordinator", "template.yaml" ]
