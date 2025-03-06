#!/usr/bin/env bash

REPLICAS=${1:-5}
echo "Scaling app service to $REPLICAS replicas..."
docker compose up -d --scale app=$REPLICAS
