FROM python:3.10-bullseye

WORKDIR /usr/src/project

# Install required packages, including unixodbc
RUN apt-get update && apt-get install -y unixodbc 

###### fix locales ######
# Install locales package
RUN apt-get update && \
    apt-get install -y locales

# Generate the en_US.UTF-8 locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LC_ALL=en_US.UTF-8

# Set environment variables for locale
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
###### fix locales ######

##### microsoft this is to make SCCM endpoint work ####
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/microsoft-prod.list
#### RUN apt update
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
RUN mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
RUN apt update && ACCEPT_EULA=Y apt-get install -y msodbcsql18
##### microsoft this is to make SCCM endpoint work ####

RUN mkdir -p /usr/src/venvs && python -m venv /usr/src/venvs/app-main

COPY requirements.txt /usr/src/

RUN /usr/src/venvs/app-main/bin/pip install --upgrade pip && \
    /usr/src/venvs/app-main/bin/pip install -r /usr/src/requirements.txt

# create a pip requirements file, based on the current environment
RUN mkdir -p /usr/src/project/app-main && \
    /usr/src/venvs/app-main/bin/pip freeze > /usr/src/project/app-main/requirements.txt

# install ping utils
RUN apt-get update && apt-get install -y iputils-ping tree

# Install MariaDB client
RUN apt-get update && apt-get install -y mariadb-client && rm -rf /var/lib/apt/lists/*