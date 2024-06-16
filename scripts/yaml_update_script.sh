#!/bin/bash

# 업데이트할 SERVICE_NAME 값 설정
NEW_SERVICE_NAME="$1"

# 현재 SERVICE_NAME 값 설정
CURRENT_SERVICE_NAME="${SERVICE_NAME}"

# docker-compose 파일의 경로
DOCKER_COMPOSE_TEMPLATE="docker-compose.template.yaml"
DOCKER_COMPOSE_OUTPUT="docker-compose.yaml"

# docker-compose 파일에서 SERVICE_NAME을 업데이트하여 임시 파일에 저장
sed "s/\${SERVICE_NAME}/${NEW_SERVICE_NAME}/g" "${DOCKER_COMPOSE_TEMPLATE}" > "${DOCKER_COMPOSE_OUTPUT}"

echo "Saved updated docker-compose file to ${DOCKER_COMPOSE_OUTPUT}."
