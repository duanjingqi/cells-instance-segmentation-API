# Ubuntu system
FROM ubuntu:latest

RUN /bin/bash -c 'apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata'

ENV TZ='America/Los_Angeles'

# Paths
ENV PRJ_PATH=/Projects
WORKDIR $PRJ_PATH

ENV APP_PATH=$PRJ_PATH/CellSegger
RUN /bin/bash -c 'mkdir ${APP_PATH}'

# Copy the git content to the docker image
COPY . ${APP_PATH}

# Install Python3, pip3 and Cell Segger dependencies
RUN /bin/bash -c 'apt-get update && \
apt-get install -y python3-dev python3-pip git apturl && \
cd /usr/local/bin && \
ln -s /usr/bin/python3 python && \
pip3 --no-cache-dir install --upgrade pip && \
rm -rf /var/lib/apt/lists/* && \
pip3 install -r ${APP_PATH}/requirements.txt'

# Set environment variables
ENV PATH '${PATH}:/usr/local/bin'
ENV PYTHONPATH '${PYTHONPATH}:${APP_PATH}/api;${APP_PATH}/unet;${APP_PATH}/tests;${APP_PATH}'

EXPOSE 3000