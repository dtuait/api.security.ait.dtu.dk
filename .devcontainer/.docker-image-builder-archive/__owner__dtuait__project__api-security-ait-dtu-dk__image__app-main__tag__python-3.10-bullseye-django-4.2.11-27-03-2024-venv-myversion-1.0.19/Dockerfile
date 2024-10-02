FROM python:3.10-bullseye

# Default arguments
ARG USERNAME=dockeruser
ARG PASSWORD=dockerpass
ARG USER_UID=65000
ARG USER_GID=$USER_UID

# Create the user with the specified username, UID, and GID, and set the password
RUN useradd -u $USER_UID -U -d /home/$USERNAME -s /bin/bash $USERNAME && \
    echo "$USERNAME:$PASSWORD" | chpasswd && \
    mkdir -p /home/$USERNAME && \
    chown $USER_UID:$USER_GID /home/$USERNAME

# Create the working directory with appropriate permissions
RUN mkdir -p /usr/src/project && chown $USER_UID:$USER_GID /usr/src/project

WORKDIR /usr/src/project

RUN apt-get update && apt-get install -y \
    unixodbc \
    locales \
    wget \
    gnupg2 \
    iputils-ping \
    tree \
    mariadb-client \
    gosu \
    sudo \
    bash \
    nano \
    && rm -rf /var/lib/apt/lists/*

###### fix locales ######
# Generate the en_US.UTF-8 locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LC_ALL=en_US.UTF-8

# Set environment variables for locale
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
###### fix locales ######

##### microsoft this is to make SCCM endpoint work ####
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/microsoft-prod.list
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
RUN mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
RUN apt update && ACCEPT_EULA=Y apt-get install -y msodbcsql18
##### microsoft this is to make SCCM endpoint work ####

# Setup Python virtual environment
RUN mkdir -p /usr/src/venvs && python -m venv /usr/src/venvs/app-main

COPY requirements.txt /usr/src/

RUN /usr/src/venvs/app-main/bin/pip install --upgrade pip && \
    /usr/src/venvs/app-main/bin/pip install -r /usr/src/requirements.txt

# create a pip requirements file, based on the current environment
RUN mkdir -p /usr/src/project/app-main && \
    /usr/src/venvs/app-main/bin/pip freeze > /usr/src/project/app-main/requirements.txt

# Allow the user to run sudo without a password
RUN echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Run app.py when the container launches
CMD ["/bin/bash"]
