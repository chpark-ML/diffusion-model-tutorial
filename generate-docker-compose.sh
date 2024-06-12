# script.sh
#!/bin/bash

# .env 파일을 읽어서 환경 변수로 설정
while IFS= read -r line; do
    export "$line"
done < .env

envsubst < docker-compose.template.yaml > $DOCKER_COMPOSE_NAME