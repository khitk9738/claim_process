# pull official base image
# `FROM python:3.11-slim-buster` is a Dockerfile instruction that specifies the base image for the Docker container. In this case, it is pulling the official Python 3.11 slim image based on the Debian Buster operating system. This base image provides a minimal Python environment for running Python applications within a container.
# The `FROM` instruction is always the first instruction in a Dockerfile and specifies the base image that the Docker container will be built from.
# The `python:3.11-slim-buster` image is a slim version of the Python 3.11 image based on the Debian Buster operating system. The slim version of the image contains a minimal set of packages and dependencies, making it smaller in size compared to the full version of the image.
# The `python:3.11-slim-buster` image is an official image provided by the Python Software Foundation and is available on the Docker Hub registry.
FROM python:3.11-slim-buster

# set working directory
# The `WORKDIR /project` instruction in a Dockerfile sets the working directory for any subsequent instructions in the Dockerfile. In this case, it sets the working directory to `/project` within the Docker container. This means that any commands or actions executed in the Dockerfile after this instruction will be relative to the `/project` directory unless explicitly specified otherwise. It helps organize the files and commands within the container and simplifies the paths used in subsequent instructions.
# The `WORKDIR` instruction is used to set the working directory within the Docker container. It is similar to the `cd` command in a shell script and changes the current working directory for subsequent instructions in the Dockerfile.
WORKDIR /project

# set environment variables
# The lines `ENV PYTHONDONTWRITEBYTECODE 1` and `ENV PYTHONUNBUFFERED 1` are setting environment variables within the Docker container.
# The `PYTHONDONTWRITEBYTECODE` environment variable is set to `1` to prevent Python from writing pyc files to disc.
# The `PYTHONUNBUFFERED` environment variable is set to `1` to prevent Python from buffering stdout and stderr.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
# The `RUN apt-get update \ && apt-get -y install netcat gcc postgresql \ && apt-get clean` command is performing the following actions:
# 1. Update the package list using the `apt-get update` command.
# 2. Install the `netcat`, `gcc`, and `postgresql` packages using the `apt-get -y install` command.
# 3. Clean up the package cache using the `apt-get clean` command.
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

# install python dependencies
# These lines of code are performing the following actions:
# 1. Copy the `requirements.txt` and `requirements-test.txt` files from the current build context into the `/project` directory within the Docker container.
# 2. Install the Python dependencies listed in the `requirements.txt` and `requirements-test.txt` files using the `pip` package manager.
# 3. Upgrade the `pip` package manager to the latest version.
RUN pip install --upgrade pip
COPY requirements.txt .
COPY requirements-test.txt .
RUN pip install -r requirements.txt
RUN pip install -r requirements-test.txt

# add app
# `COPY ./project .` is copying the contents of the `project` directory from the current build context into the `/project` directory within the Docker container. This step is typically used to add application code, configuration files, or any other necessary files to the container image during the build process.
COPY ./project .
