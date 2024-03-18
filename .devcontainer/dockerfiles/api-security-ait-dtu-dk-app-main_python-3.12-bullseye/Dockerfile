# Use Python 3.12.2 on Debian Bullseye as the base image
FROM python:3.12

# Create a directory for the project
RUN mkdir -p /mnt/project

# Set the working directory
WORKDIR /mnt/project

# Update packages and install unixodbc
RUN apt-get update && apt-get install -y unixodbc

###### fix locales ######
# Install locales package and generate the en_US.UTF-8 locale
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LC_ALL=en_US.UTF-8

# Set environment variables for locale
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
###### fix locales ######

##### Microsoft packages (for compatibility, update the repository to match Debian Bullseye) #####
# Add the Microsoft package repository for Debian Bullseye
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/microsoft-prod.list

# Import the Microsoft GPG key
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

# Install msodbcsql18
RUN apt update && ACCEPT_EULA=Y apt-get install -y msodbcsql18
##### Microsoft packages #####

# Install ping utilities
RUN apt-get update && apt-get install -y iputils-ping
