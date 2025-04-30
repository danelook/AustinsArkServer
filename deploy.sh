#!/bin/bash

# Exit if any command fails
set -e

# Define sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

# Build docker images
echo "Building Docker images..."
# sensor images
for SENSOR in "${SENSORS[@]}"; do
    echo "Building image for $SENSOR..."
    docker build -f Docker/sensors/${SENSOR}/Dockerfile -t ${SENSOR}:latest .
done
# kafka_consumer image
docker build -f Docker/consumer/Dockerfile -t kafka_consumer:latest .

# Kubernetes
# sensor deployments
for SENSOR in "${SENSORS[@]}"; do
    echo "Deploying $SENSOR to Kubernetes..."
    kubectl apply -f "k8s/sensors/${SENSOR}.yaml"
done
# kakfa broker deployment
kubectl apply -f "k8s/kafka/kafka_stack.yaml"

# mysql deployment
echo "Deploying MySQL to Kubernetes..."
kubectl apply -f "k8s/databases/mysql_deployment.yaml"

# kafka_consumer deployment 
kubectl apply -f "k8s/kafka/kafka_consumer_deployment.yaml"

echo "All sensors deployed successfully!"  