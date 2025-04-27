#!/bin/bash

set -e  # Exit immediately if any command fails

# List of sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

echo "Tearing down existing Kubernetes deployments..."

# Teardown Kubernetes deployments
for SENSOR in "${SENSORS[@]}"; do
  echo "Deleting deployment and service for $SENSOR..."
  kubectl delete -f "k8s/sensors/${SENSOR}.yaml" || echo "$SENSOR resources not found, skipping..."
done

echo "Building Docker images..."

# Build Docker images for each sensor
for SENSOR in "${SENSORS[@]}"; do
  echo "Building image for $SENSOR..."
  docker build -t "${SENSOR}:latest" -f "Docker/sensors/${SENSOR}/Dockerfile" .
done

echo "Applying Kubernetes configurations..."

# Apply the updated Kubernetes configurations
for SENSOR in "${SENSORS[@]}"; do
  echo "Deploying $SENSOR to Kubernetes..."
  kubectl apply -f "k8s/sensors/${SENSOR}.yaml"
done

echo "Redeployment complete!"
