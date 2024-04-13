FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

# Copy only the wheel file
COPY dist/*.whl /tmp/*.whl

# Install the package
RUN pip install /tmp/*.whl && rm /tmp/*.whl

RUN groupadd -r assistantuser && useradd -r -m -g assistantuser assistantuser

WORKDIR /home/assistantuser

USER assistantuser

ENTRYPOINT [ "private-assistant-skill-coordinator", "template.yaml" ]
