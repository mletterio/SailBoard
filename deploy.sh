#!/bin/bash
set -e

REMOTE="${1:?Usage: ./deploy.sh user@host}"
IMAGE="sailboard"

docker buildx build --platform linux/arm64 --tag "$IMAGE" --load .

docker save "$IMAGE" | gzip | ssh "$REMOTE" "
    gunzip | docker load
    docker stop $IMAGE 2>/dev/null || true
    docker rm $IMAGE 2>/dev/null || true
    docker run -d --name $IMAGE --restart unless-stopped \
        --device /dev/gpiomem --device /dev/spidev0.0 $IMAGE
"