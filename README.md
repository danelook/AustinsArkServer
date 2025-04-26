# AustinsArkServer

## Building images using Dockerfile(s)
```bash
docker build -t {image-to-build}:latest -f Docker/Dockerfile.humidity_sensor .
```
For example: humidity_sensor image
```bash
docker build -t humidity_sensor:latest -f Docker/sensors/humidity/Dockerfile .
```

## Spinning up deployments using k8s deployments.yml (humidity_sensor example)
```bash
kubectl apply -f ./k8s/sensors/humidity_sensor-deployment.yaml 
```