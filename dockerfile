FROM alpine:3.17

ENV PATH '${PATH}:/usr/local/bin'

ENV PYTHON_VERSION 3.9.17

ENV PRJ_PATH=/Projects
WORKDIR $PRJ_PATH

ENV APP_PATH=$PRJ_PATH/CellSegger
RUN /bin/bash -c 'mkdir ${APP_PATH}'

COPY . ${APP_PATH}

RUN /bin/bash -c 'pip3 install -r ${APP_PATH}/requirements.txt'

ENV PYTHONPATH '${PYTHONPATH}:${APP_PATH}/api;${APP_PATH}/unet;${APP_PATH}/tests;${APP_PATH}'

# ENV PYTHONPATH=/api
# WORKDIR /api

# EXPOSE 8000

# ENTRYPOINT ['uvicorn']
# CMD ['api.main:app', '--host', '0.0.0.0']