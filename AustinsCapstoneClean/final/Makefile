# Build all Docker images
build:
	docker build -t humidity-sensor Docker/sensors/humidity_sensor
	docker build -t motion-sensor Docker/sensors/motion_sensor
	docker build -t temperature-sensor Docker/sensors/temperature_sensor
	docker build -t kafka-consumer Docker/consumer

# Apply Kubernetes manifests
deploy:
	kubectl apply -f k8s/databases/mysql_deployment.yaml
	kubectl apply -f k8s/kafka/kafka_stack.yaml
	kubectl apply -f k8s/sensors/
	kubectl apply -f k8s/kafka/kafka_consumer_deployment.yaml

# Delete all Kubernetes resources
clean:
	kubectl delete -f k8s/sensors/ --ignore-not-found=true
	kubectl delete -f k8s/kafka/ --ignore-not-found=true
	kubectl delete -f k8s/databases/ --ignore-not-found=true

# Rebuild and redeploy everything
redeploy: clean build deploy
