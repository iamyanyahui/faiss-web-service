#!/bin/sh

BASE_PATH=$(cd `dirname $0`; pwd)
ROOT=${BASE_PATH}/..

export FAISS_WEB_SERVICE_CONFIG=${FAISS_WEB_SERVICE_CONFIG:-${ROOT}/faiss_web_service_config/faiss_index_local_file_test.py}

development () {
  python ${ROOT}/src/app.py
}

production () {
    #mkdir -p /var/log/faiss_web_service

    uwsgi \
        --http :5000 \
        --chdir ${ROOT}/src \
        --module app:app \
        --master \
        --processes 4 \
        --threads 2 \
        --metric-dir ${HOME}/SourceTree/faiss-web-service/env/service \
        --logto ./env/log/app.log \
        --safe-pidfile ${HOME}/SourceTree/faiss-web-service/env/master_project.pid
}

case "${1}" in
   "prod") production ;;
   *) development ;;
esac
