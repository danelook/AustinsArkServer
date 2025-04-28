#!/bin/bash

set -e  # Exit immediately if any command fails

# List of sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

echo "Tearing down existing Kubernetes deployments..."

# Teardown sensor deployments
for SENSOR in "${SENSORS[@]}"; do
  echo "Deleting deployment and service for $SENSOR..."
  kubectl delete -f "k8s/sensors/${SENSOR}.yaml" || echo "$SENSOR resources not found, skipping..."
done

# Teardown Kafka-related deployments
echo "Deleting Kafka stack..."
kubectl delete -f "k8s/kafka/kafka_stack.yaml" || echo "Kafka stack resources not found, skipping..."

echo "Deleting Kafka consumer deployment..."
kubectl delete -f "k8s/kafka/kafka_consumer_deployment.yaml" || echo "Kafka consumer resources not found, skipping..."

echo "Building Docker images..."

# Build Docker images for each sensor
for SENSOR in "${SENSORS[@]}"; do
  echo "Building image for $SENSOR..."
  docker build -t "${SENSOR}:latest" -f "Docker/sensors/${SENSOR}/Dockerfile" .
done

# Build Docker image for Kafka consumer
echo "Building image for kafka_consumer..."
docker build -t kafka_consumer:latest -f Docker/consumer/Dockerfile .

echo "Applying Kubernetes configurations..."

# Apply sensor deployments
for SENSOR in "${SENSORS[@]}"; do
  echo "Deploying $SENSOR to Kubernetes..."
  kubectl apply -f "k8s/sensors/${SENSOR}.yaml"
done

# Apply Kafka deployments
echo "Deploying Kafka stack..."
# kubectl apply -f "k8s/kafka/kafka_stack.yaml"

echo "Deploying Kafka consumer..."
# kubectl apply -f "k8s/kafka/kafka_consumer_deployment.yaml"

echo "Redeployment complete!"
