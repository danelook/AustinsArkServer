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
We are able to currently establish a connection between the kafka_consumer and the mysql pod, but we need to manually delete/re-apply the kafka_consumer in order for it to make the connection. This could be because the mysql pod needs time to spin up before it is ready to accept connections and the kafka_consumer tries to connect too early. 
## Next steps: 
1. Implement retry logic in kafka_consumer to retry connecting to the mysql pod until a connection is established before consuming topics/messages
2. Implement establishing infrastructure within kafka_consumer, i.e. databases/tables/primary keys/etc, in mysql db before messages are imported to mysql from kafka_consumer
3. test/verify importing works as intended with 3 consumers then scale up replicas

# View top logs
```bash
kubectl logs <pod-name> | head -n X
```