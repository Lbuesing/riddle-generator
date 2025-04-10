FROM python:3.11-slim-bookworm
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install setuptools
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src


# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app
# RUN mkdir -p /usr/local/app/output

ENTRYPOINT ["python", "src/main.py"]
