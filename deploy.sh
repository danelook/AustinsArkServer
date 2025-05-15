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
  
# Prometheus   
kubectl apply -f "k8s/prometheus.yaml"
kubectl rollout status deployment/prometheus

# Prometheus and dashboards configmap rollout
echo "--------------------------"
echo "Deploying to Prometheus configmap and dashboards configmap..."
echo "--------------------------"
kubectl apply -f "k8s/dashboards/temp_dash.yaml"
kubectl apply -f "k8s/dashboards/humidity_dash.yaml"
kubectl apply -f "k8s/dashboards/motion_dash.yaml"
kubectl apply -f "k8s/grafana_dash_provider.yaml"
kubectl apply -f "k8s/promethues_source.yaml"

#grafana deployment
kubectl apply -f "k8s/grafana/grafana.yaml"
kubectl rollout status deployment/grafana

# mysql deployment 
kubectl apply -f "k8s/databases/mysql_deployment.yaml"
kubectl rollout status deployment/mysql

# mongodb deployment
kubectl apply -f "k8s/databases/mongodb-deployment.yaml"
kubectl rollout status deployment/mongodb

# kafka_consumer deployment 
kubectl apply -f "k8s/kafka/kafka_consumer_deployment.yaml"

echo "All deployments deployed successfully!"  

# Port forwarding
echo "--------------------------"
echo "Port-forwarding Prometheus and Grafana..."
echo "--------------------------"
kubectl port-forward svc/prometheus 9090:9090 > /dev/null 2>&1 &
kubectl port-forward svc/grafana 3000:80 > /dev/null 2>&1 &