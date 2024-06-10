# Set service name
SERVICE_NAME = diffusion-model-tutorial
RESEARCH_NAME = research
DEPLOY_NAME = deploy
SERVICE_NAME_BASE = ${SERVICE_NAME}-base
SERVICE_NAME_RESEARCH = ${SERVICE_NAME}-${RESEARCH_NAME}
SERVICE_NAME_DEPLOY = ${SERVICE_NAME}-${DEPLOY_NAME}

# Set command
COMMAND_BASE = /bin/bash
COMMAND_RESEARCH = /bin/zsh
COMMAND_DEPLOY = /bin/bash

# Get IDs
GID = $(shell id -g)
UID = $(shell id -u)
GRP = $(shell id -gn)
USR = $(shell id -un)

# Get docker image name
IMAGE_NAME_BASE = ${SERVICE_NAME}-base:1.0.0
IMAGE_NAME_RESEARCH = ${SERVICE_NAME_RESEARCH}-${USR}:1.0.0
IMAGE_NAME_DEPLOY = ${SERVICE_NAME_DEPLOY}:1.0.0

# Get docker container name
CONTAINER_NAME_RESEARCH = ${SERVICE_NAME_RESEARCH}-${USR}
CONTAINER_NAME_DEPLOY = ${SERVICE_NAME_DEPLOY}

# Docker build context
DOCKER_BUILD_CONTEXT_PATH = .
DOCKERFILE_NAME_BASE = dockerfile_base
DOCKERFILE_NAME_RESEARCH = dockerfile_research
DOCKERFILE_NAME_DEPLOY = dockerfile_deploy
DOCKER_COMPOSE_NAME = docker-compose.yaml
ENV_FILE_PATH = .env
OVERRIDE_FILE = docker-compose.override.yaml

# Set working & current path 
WORKDIR_PATH = /opt/${SERVICE_NAME}
CURRENT_PATH = $(shell pwd)

# Set enviornments
ENV_TEXT = "$\
	GID=${GID}\n$\
	UID=${UID}\n$\
	GRP=${GRP}\n$\
	USR=${USR}\n$\
	SERVICE_NAME=${SERVICE_NAME}\n$\
	IMAGE_NAME_BASE=${IMAGE_NAME_BASE}\n$\
	IMAGE_NAME_RESEARCH=${IMAGE_NAME_RESEARCH}\n$\
	IMAGE_NAME_DEPLOY=${IMAGE_NAME_DEPLOY}\n$\
	CONTAINER_NAME_RESEARCH=${CONTAINER_NAME_RESEARCH}\n$\
	CONTAINER_NAME_DEPLOY=${CONTAINER_NAME_DEPLOY}\n$\
	WORKDIR_PATH=${WORKDIR_PATH}\n$\
	CURRENT_PATH=${CURRENT_PATH}\n$\
	DOCKER_BUILD_CONTEXT_PATH=${DOCKER_BUILD_CONTEXT_PATH}\n$\
	DOCKERFILE_NAME_BASE=${DOCKERFILE_NAME_BASE}\n$\
	DOCKERFILE_NAME_RESEARCH=${DOCKERFILE_NAME_RESEARCH}\n$\
	DOCKERFILE_NAME_DEPLOY=${DOCKERFILE_NAME_DEPLOY}\n$\
	DOCKER_COMPOSE_NAME=${DOCKER_COMPOSE_NAME}\n$\"
${ENV_FILE_PATH}:
	printf ${ENV_TEXT} >> ${ENV_FILE_PATH}

# env  
env: ${ENV_FILE_PATH}

vs:  # Preempts `.vscode-server` directory ownership issues.
	@mkdir -p ${HOME}/.vscode-server

OVERRIDE_BASE = "$\
services:$\
\n  ${SERVICE_NAME_RESEARCH}:$\
\n    volumes:$\
\n      - ${HOME}:/mnt/home$\
\n"

over:
	printf ${OVERRIDE_BASE} >> ${OVERRIDE_FILE}

generate: 
	export $(grep -v '^#' .env | xargs) && envsubst < docker-compose.template.yaml > docker-compose.yaml

# base docker
build-base:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} up --build -d ${SERVICE_NAME_BASE}
up-base:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} up -d ${SERVICE_NAME_BASE}
exec-base:
	DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} exec ${SERVICE_NAME_BASE} ${COMMAND_BASE}
start-base:
	docker compose -f ${DOCKER_COMPOSE_NAME} start ${SERVICE_NAME_BASE}
down-base:
	docker compose -f ${DOCKER_COMPOSE_NAME} down
run-base:
	docker compose -f ${DOCKER_COMPOSE_NAME} run ${SERVICE_NAME_BASE} ${COMMAND_BASE}
ls-base:
	docker compose ls -a

# research docker
build-${RESEARCH_NAME}: build-base
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml up --build -d ${SERVICE_NAME_RESEARCH}
up-${RESEARCH_NAME}:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml up -d ${SERVICE_NAME_RESEARCH}
exec-${RESEARCH_NAME}:
	DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml exec ${SERVICE_NAME_RESEARCH} ${COMMAND_RESEARCH}
start-${RESEARCH_NAME}:
	docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml start ${SERVICE_NAME_RESEARCH}
down-${RESEARCH_NAME}:
	docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml down
run-${RESEARCH_NAME}:
	docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml run ${SERVICE_NAME_RESEARCH} ${COMMAND_RESEARCH}
ls-${RESEARCH_NAME}:
	docker compose ls -a

# deploy docker
build-${DEPLOY_NAME}: build-base
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml up --build -d ${SERVICE_NAME_DEPLOY}
up-${DEPLOY_NAME}:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml up -d ${SERVICE_NAME_DEPLOY}
exec-${DEPLOY_NAME}:
	DOCKER_BUILDKIT=1 docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml exec ${SERVICE_NAME_DEPLOY} ${COMMAND_DEPLOY}
start-${DEPLOY_NAME}:
	docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml start ${SERVICE_NAME_DEPLOY}
down-${DEPLOY_NAME}:
	docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml down
run-${DEPLOY_NAME}:
	docker compose -f ${DOCKER_COMPOSE_NAME} -f docker-compose.override.yaml run ${SERVICE_NAME_DEPLOY} ${COMMAND_DEPLOY}
ls-${DEPLOY_NAME}:
	docker compose ls -a
