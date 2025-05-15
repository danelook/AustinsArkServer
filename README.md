# Project ArkSense
## Notes
We are currently able to run a kubernetes cluster that spawns 3 different sensor types. Each sensor sends/produces messages to a different topic which is then routed through a kafka-broker system and ultimately consumed by a kafka_consumer. The kafka_consumer is able to establish a connection to a spawned mySQL pod with pre-established infrastructure and insert sensor data into said infrastructure. The kafka_consumer is also able to establish a connection to a spawned mongodb pod and insert simulated server logs to be stored for monitoring/observability. 

## Requirements: 
This system was developed on Windows using the WSL compatability layer (Distro:Ubuntu) and also the following tools: 
* Docker-Desktop
* Kubernetes (Docker-Desktop) 

## How to start up K8s cluster:
### Run deploy.sh
Make sure the script is executable on your system first. If it is not executable...
```bash
chmod +x ./deploy.sh
```
Then run the script.
```bash
./deploy.sh
```

### Taking the cluster down: 
Make sure the script is executable on your system first. If it is not executable...
```bash
chmod +x ./teardown.sh
```
Then run the script.
```bash
./teardown.sh
``` 

## Helpful commands:
### View top logs
```bash
kubectl logs <pod-name> | head -n X
```
### Scaling replicas per sensor
Replace {sensor_type} with whichever sensor you want to scale up or down.
Replace {number} with number of replicas you want to scale to.
```bash
kubectl scale deployment {sensor_type}-sensor --replicas={number}
```

## Port-forward command to view interactive kafka-broker-ui in browser
```bash
kubectl port-forward svc/kafka-ui 8080:8080
```

# Real world application to our project
1. Environment sensors to notify about PNC branch location busy-ness. For example, Planet Fitness has a "Crowd Meter" that we could relate to with what our system does. 