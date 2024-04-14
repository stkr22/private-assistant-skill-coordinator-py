FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

# Copy only the wheel file
COPY dist/$WHEEL_FILE.whl /tmp/$WHEEL_FILE.whl

# Install the package
RUN pip install /tmp/$WHEEL_FILE.whl && \
    rm /tmp/$WHEEL_FILE.whl

RUN groupadd -r assistantuser && useradd -r -m -g assistantuser assistantuser

WORKDIR /home/assistantuser

USER assistantuser

ENTRYPOINT [ "private-assistant-skill-coordinator", "template.yaml" ]
