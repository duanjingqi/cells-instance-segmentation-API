FROM ubuntu:rolling

ENV PRJ_PATH=/Projects
WORKDIR $PRJ_PATH

ENV APP_PATH=$PRJ_PATH/CellSegger
RUN /bin/bash -c 'mkdir ${APP_PATH}'

COPY . ${APP_PATH}

RUN /bin/bash -c 'apt-get update && \
apt-get install python3-dev python3-pip -y && \
pip3 install -r ${APP_PATH}/requirements.txt'

ENV PYTHONPATH '${PYTHONPATH}:${APP_PATH}/api;${APP_PATH}/unet;${APP_PATH}/tests;${APP_PATH}'

# ENV PYTHONPATH=/api
# WORKDIR /api

# EXPOSE 8000

# ENTRYPOINT ['uvicorn']
# CMD ['api.main:app', '--host', '0.0.0.0']