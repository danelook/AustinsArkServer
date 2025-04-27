#!/bin/bash

# Exit if any command fails
set -e

# Define sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

# Build docker images
echo "Building Docker images..."
for SENSOR in "${SENSORS[@]}"; do
    echo "Building image for $SENSOR..."
    docker build -f Docker/sensors/${SENSOR}/Dockerfile -t ${SENSOR}:latest .
done

# Apply k8s deployments
for SENSOR in "${SENSORS[@]}"; do
    echo "Deploying $SENSOR to Kubernetes..."
    kubectl apply -f "k8s/sensors/${SENSOR}.yaml"
done

echo "All sensors deployed successfully!"