#!/bin/bash

set -e  # Exit if any command fails

# List of sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

echo "Tearing down Kubernetes deployments..."

# Teardown sensor deployments
for SENSOR in "${SENSORS[@]}"; do
  echo "Deleting deployment and service for $SENSOR..."
  kubectl delete -f "k8s/sensors/${SENSOR}.yaml" || echo "$SENSOR resources not found, skipping..."
done

# Teardown log_producer deployment
echo "Deleting log_producer..."
kubectl delete -f "k8s/log/log_producer-deployment.yaml" || echo "Log producer resources not found, skipping..."

# Teardown prometheus deployment
echo "Deleting Prometheus..."
kubectl delete -f "k8s/prometheus.yaml" || echo "Prometheus resources not found, skipping..."

# Teardown Kafka-related deployments
echo "Deleting Kafka stack..."
kubectl delete -f "k8s/kafka/kafka_stack.yaml" || echo "Kafka stack resources not found, skipping..."

echo "Deleting Kafka consumer deployment..."
kubectl delete -f "k8s/kafka/kafka_consumer_deployment.yaml" || echo "Kafka consumer resources not found, skipping..."

# Teardown mySQL deployment
echo "Deleting MySQL..."
kubectl delete -f "k8s/databases/mysql_deployment.yaml" || echo "MySQL resources not found, skipping..."

# Teardown of mongodb deployment
echo "Deleting MongoDB..."
kubectl delete -f "k8s/databases/mongodb-deployment.yaml" || echo "MongoDB resources not found, skipping..."

echo "Cleanup complete!"
