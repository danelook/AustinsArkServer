# Project ArkSense
# Notes
We are currently able to run a kubernetes cluster that spawns 3 different sensor types. Each sensor sends/produces messages to a different topic which is then routed through a kafka-broker system and ultimately consumed by a kafka_consumer. The kafka_consumer is able to establish a connection to a spawned mySQL pod with pre-established infrastructure and insert sensor data into said infrastructure. The kafka_consumer is also able to establish a connection to a spawned mongodb pod and insert simulated server logs to be stored for monitoring/observability.

## Next steps:   
1. Implement prometheus metric exporting inside kafka_consumer.
2. Build custom dashboards to allow for monitoring and observability of the system and implement configMap for data persistence/structure.
3. Documentation for entire system
4. Put together presentation slides & establish game-plan for presentation.

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

# Notable Errors: 
1. Deleting the kafka-broker pod basically stops messages from flowing through. Producers still produce messages, the kafka-consumer still stays up and running, and the databases are still fully functional, but the flow of messages stops and doesn't continue once the broker is deleted. Even if it a new broker is spawned, the messages don't continue. Something to look into. 

# View top logs
```bash
kubectl logs <pod-name> | head -n X
```

# Monitoring and Observability
In order to view prometheus and Grafana a few steps have to be taken. 
1. port forward prometheus using the following command: 
```bash
kubectl port-forward service/prometheus-service 9090:9090
```
2. port forward grafana using the following command: 
```bash
kubectl port-forward svc/grafana 3000:80
```
3. Add prometheus as a data source on grafana
    3a. Enter the following into the Promethus server url: http://prometheus-service:9090
    3b. Save and test the data source

4. Create dashboards. 