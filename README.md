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
## Taking the cluster down: 
Make sure the script is executable on your system first. If it is not executable...
```bash
chmod +x ./teardown.sh
```
Then run the script.
```bash
./teardown.sh
```