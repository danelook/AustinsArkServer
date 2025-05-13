# AustinsArkServer
# How to start up K8s cluster:
## Run deploy.sh
Make sure the script is executable on your system first. If it is not executable...
```bash
chmod +x ./deploy.sh
```
Then run the script.
```bash
./deploy.sh
```
## Port-forward command to view interactive kafka-ui in browser
```bash
kubectl port-forward svc/kafka-ui 8080:8080
```
## Scaling replicas per sensor
Replace {sensor_type} with whichever sensor you want to scale up or down.
Replace {number} with number of replicas you want to scale to.
```bash
kubectl scale deployment {sensor_type}-sensor --replicas={number}
```

## Taking the cluster down: 
Make sure the script is executable on your system first. If it is not executable...
```bash
chmod +x ./teardown.sh
```
Then run the script.
```bash
./teardown.sh
```

# Notes
We are currently able to run a kubernetes cluster that spawns 3 different sensor types. Each sensor sends/produces messages to a different topic which is then routed through a kafka-broker system and ultimately consumed by a kafka_consumer. The kafka_consumer is able to establish a connection to a spawned mySQL pod with pre-established infrastructure. 
## Next steps:   
1. Implement prometheus metric exporting inside each sensor, kafka_consumer, and mySQL pod.
2. Connect Grafana to prometheus metrics and build custom dashboards to allow for monitoring and observability of the system.
3. Documentation for entire system
4. Put together presentation slides & establish game-plan for presentation.

# Notable Errors: 
1. Deleting the kafka-broker pod basically stops messages from flowing through. Producers still produce messages, the kafka-consumer still stays up and running, and the databases are still fully functional, but the flow of messages stops and doesn't continue once the broker is deleted. Even if it a new broker is spawned, the messages don't continue. Something to look into. 

# View top logs
```bash
kubectl logs <pod-name> | head -n X
```