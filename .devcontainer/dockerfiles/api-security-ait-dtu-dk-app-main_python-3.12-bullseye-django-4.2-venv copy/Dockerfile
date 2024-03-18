FROM python:3.12-bullseye

WORKDIR /usr/src/project

# Install system dependencies including unixodbc-dev for pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    iputils-ping \
    locales \
    wget \
    gnupg2 && \
    # Fix locales
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LC_ALL=en_US.UTF-8 && \
    # Setup Microsoft repositories for Debian Bullseye
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg && \
    apt update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Set environment variables for locale
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Create a directory for the virtual environment and create it
RUN mkdir -p /usr/src/venvs && python -m venv /usr/src/venvs/app-main

# Ensure your requirements.txt is present in the context
COPY requirements.txt /usr/src/project/

# Activate the virtual environment and install dependencies from requirements.txt
RUN /usr/src/venvs/app-main/bin/pip install --upgrade pip && \
    /usr/src/venvs/app-main/bin/pip install -r /usr/src/project/requirements.txt
