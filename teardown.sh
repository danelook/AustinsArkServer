#!/bin/bash

set -e  # Exit if any command fails

# List of sensors
SENSORS=("humidity_sensor" "motion_sensor" "temperature_sensor")

echo "Tearing down Kubernetes deployments..."

for SENSOR in "${SENSORS[@]}"; do
  echo "Deleting deployment and service for $SENSOR..."
  kubectl delete -f "k8s/sensors/${SENSOR}.yaml" || echo "$SENSOR resources not found, skipping..."
done

echo "Cleanup complete!"
