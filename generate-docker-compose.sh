# script.sh
#!/bin/bash
export $(grep -v '^#' .env | xargs)
envsubst < docker-compose.template.yaml > $DOCKER_COMPOSE_NAME