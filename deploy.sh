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

# log_producer image
docker build -f Docker/log/Dockerfile -t log_producer:latest .
# kafka_consumer image
docker build -f Docker/consumer/Dockerfile -t kafka_consumer:latest .

# Kubernetes
# sensor deployments
for SENSOR in "${SENSORS[@]}"; do
    echo "Deploying $SENSOR to Kubernetes..."
    kubectl apply -f "k8s/sensors/${SENSOR}.yaml"
done
# log_producer deployment
kubectl apply -f "k8s/log/log_producer-deployment.yaml"
# kakfa broker deployment
kubectl apply -f "k8s/kafka/kafka_stack.yaml"

# ConfigMap for MySQL initialization
echo "Creating ConfigMap for MySQL initialization..."

kubectl create configmap mysql-initdb-config \
  --from-file=init.sql=k8s/databases/init.sql \
  --dry-run=client -o yaml | kubectl apply -f -


# mysql deployment
echo "Deploying MySQL to Kubernetes..."
kubectl apply -f "k8s/databases/mysql_deployment.yaml"

kubectl rollout status deployment/mysql

# kafka_consumer deployment 
kubectl apply -f "k8s/kafka/kafka_consumer_deployment.yaml"

echo "All sensors deployed successfully!"  