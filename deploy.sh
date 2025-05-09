#!/bin/bash

# Exit if any command fails
set -e

# Define sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

# Build docker images
echo "--------------------------"
echo "Building Docker images..."
echo "--------------------------"

# sensor images
for SENSOR in "${SENSORS[@]}"; do 
    docker build -f Docker/sensors/${SENSOR}/Dockerfile -t ${SENSOR}:latest .
done

# log_producer image
docker build -f Docker/log/Dockerfile -t log_producer:latest .

# kafka_consumer image
docker build -f Docker/consumer/Dockerfile -t kafka_consumer:latest .

# Kubernetes
# sensor deployments
echo "--------------------------"
echo "Deploying to Kubernetes..."
echo "--------------------------"
for SENSOR in "${SENSORS[@]}"; do 
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
kubectl apply -f "k8s/databases/mysql_deployment.yaml"
kubectl rollout status deployment/mysql

# mongodb deployment
kubectl apply -f "k8s/databases/mongodb-deployment.yaml"
kubectl rollout status deployment/mongodb

# kafka_consumer deployment 
kubectl apply -f "k8s/kafka/kafka_consumer_deployment.yaml"

echo "All sensors deployed successfully!"  