# Project: Arksense Documentation

## Project Overview

Project: Arksense is our group's effort to simulate an IoT environment where synthetic sensors generate data streams that are captured, processed, and analyzed in real-time. The system is designed to reflect real-world industrial applications for monitoring and observing multi-sensor environments.

This project is the culmination of the efforts of Austin Russell, Benjamin Gonzalez, Dane Look, Humberto Lopez, and Kevin Cervantes — showcasing knowledge gained from the TEKsystems 2025 PNC-SRE Bootcamp.

## Project Goals

The primary goals of Project: Arksense are to:

- Build a scalable and real-time IoT data pipeline.
- Demonstrate interoperability between multiple data systems (Kafka, MongoDB, MySQL).
- Apply core Site Reliability Engineering (SRE) principles such as automation, monitoring, and observability (via Prometheus and Grafana).

## Objectives

The following objectives were established during the planning phase of Project: Arksense:

- Simulate temperature, humidity, motion, and other configurable sensors using Python.
- Deploy all services as decoupled, containerized microservices in a Kubernetes environment.
- Generate and categorize simulated server logs into MongoDB.
- Insert and store structured sensor data in MySQL.
- Ensure data persistence in the event of service failures.
- Implement resiliency and reconnection logic within Kubernetes-managed containers.
- Monitor and visualize system metrics using Prometheus and Grafana.

## Project Scope

### Sensor Simulation

- Python-based simulation of temperature, humidity, and motion sensors.
- Each sensor acts as an independent Kafka producer.
- Deployed as containerized microservices within a Kubernetes cluster.

### Simulated Server-Log Generation

- A standalone Python-based log generator produces logs at varying severity levels (INFO, WARNING, ERROR).
- Acts as an independent Kafka producer.
- Also containerized and deployed via Kubernetes.

### Persistent Data Pipeline with Kafka

- Kafka and Zookeeper (via Confluent or Bitnami) are deployed within the Kubernetes cluster.
- Producers publish messages to specific Kafka topics.
- A single Kafka consumer processes messages and routes them to appropriate data stores.

### Data Storage

- Sensor data is stored in a MySQL database using predefined schemas.
- Log data is stored in MongoDB in an unstructured format.
- Both databases run as Kubernetes pods with persistent storage volumes to ensure data survival during restarts.

### Monitoring and Observability

- Prometheus scrapes metrics from all producers and the consumer service.
- Metrics include processing success/failure rates, log severity counts, message throughput, and real-time sensor values.
- Grafana dashboards provide real-time visualizations of collected metrics.

### Kubernetes Deployment

- All components are containerized and deployed in Kubernetes.
- System includes service discovery, health checks, inter-service communication, port forwarding, and basic resilience features (auto-restarts, scaling).

## System Architecture
### The following is a flow/architecture-hybrid diagram of Project:Arksense: 
![System Architecture/flow diagram](/diagrams/ProjectArkSense_v4.jpg)

## Tools & Technologies
- **WSL (Ubuntu Distro)** - Windows Subsystem for Linux compatability layer for development environment.
- **Python** – Used to develop sensor and log generator microservices.
- **Docker** (Docker-Desktop) – Containerized all services for consistent deployment across environments.
- **Kubernetes** (via Docker-Desktop) – Orchestrated deployment, scaling, and management of all containers.
- **Apache Kafka** – Enabled real-time message streaming between producers and consumers.
- **Zookeeper** – Coordinated Kafka brokers within the cluster.
- **MySQL** – Structured storage for simulated sensor data.
- **MongoDB** – NoSQL storage for unstructured server log events.
- **Prometheus** – Collected metrics from producers and the Kafka consumer.
- **Grafana** – Visualized Prometheus metrics on real-time dashboards.

## Set up
### Docker-Desktop
Docker-Desktop is first and foremost the most important tool necessary for running this project. Installation of Docker-Desktop can be found here: https://docs.docker.com/desktop/

Once Docker-Desktop is installed, it is required to have WSL integration enabled. This can be done by going through the following path and ensuring the appropriate box is checked: 

```
Settings (Cog icon) -> General -> Use the WSL 2 based engine
```

### Kubernetes
Kubernetes must also be installed/enabled within Docker-Desktop in order for the system to run. This option can be enabled by ensuring the appropriate toggle-switch is checked in the following path: 

```
Settings (Cog icon) -> Kubernetes -> Enable Kubernetes
```

The cluster provisioning method our team used through the duration of development was Kubeadm. Other cluster provisioning methods were not utilized/tested, so functionality may vary if methods other than Kubeadm are selected. 

### Starting the cluster via deploy.sh
An automated bash script was created to spin up all components within the kubernetes cluster and port-forward the grafana service for in-browser functionality. 

Make sure the script is executable on your system first. If it is not executable, use the following command to change the file permissions...
```bash
chmod +x ./deploy.sh
```
Then run the script.
```bash
./deploy.sh
```

### Taking the cluster down via teardown.sh: 
An automated bash script was created to tear down all components within the kubernetes cluster and clean up the system. 
An important sidenote - the teardown script does not clear the Kubernetes/Docker cache and may leave cached images/setup files present. 

Make sure the script is executable on your system first. If it is not executable, use the following command to change the file permissions...
```bash
chmod +x ./teardown.sh
```
Then run the script.
```bash
./teardown.sh
``` 

## Data flow
### The following is a diagram of the flow of simulated sensor-data from one sensor to the appropriate database in the Kubernetes cluster:
![A flow diagram of Temp_sensor data](/diagrams/Temperature_flow.jpg)
> Simulated sensor-data is produced by the sensor, sent to the kafka-broker system via topic/message, consumed by the Kafka consumer, and finally inserted into the appropriate table within the MySQL database 'sensordata'. 


### The following is a diagram of the flow of simulated server-log data from the standalone log producer to the appropriate database in the cluster:
![A flow diagram of log_producer data](/diagrams/server_logs_flow.jpg)
> Simulated log-data is produced by the standalone log-producer, sent to the kafka-broker system via topic/message, consumed by the Kafka consumer, and finally inserted into the 'server_logs' collection within the 'logdata' database. 

### The following is a diagram of the flow of metrics data to the Prometheus and Grafana services:
![A flow diagram of metric data](/diagrams/Observability_flow.jpg)
> Metrics are exported from sensors, the consumer, and the log producer to an exposed port, the Prometheus service scrapes data exposed to the exposed port, and the Prometheus service is utilized as a datasource for the Grafana service to build visualizations within dashboards.

## Testing

Testing for Project:Arksense focused primarily on validating system resilience, reliability, and core functional correctness within a Kubernetes-managed environment. While formal test cases and automation were limited, a variety of manual and scenario-based tests were conducted throughout development to ensure system behavior aligned with expectations.

### Functional Testing

- Verified that all sensor and log producer services successfully published data to Kafka topics.
- Confirmed that the Kafka consumer correctly parsed messages and routed them to either MySQL or MongoDB based on data type.
- Tested database insertions to ensure correct data formatting, schema adherence (MySQL), and document structure (MongoDB).

### Resilience & Recovery Testing

- **Pod deletion and restart**: Manually deleted various pods (sensors, consumer, databases) to observe Kubernetes auto-recovery. Verified that functionality resumed without manual intervention and that message flow remained intact.

>#### Test Case: Kafka Consumer Resilience on Restart  
>Ensure that the Kafka consumer can restart gracefully and continue processing messages without data loss.
>
>**Steps:**
>1. Start all components and allow producers to generate messages.
>2. Delete the Kafka consumer pod using `kubectl delete pod <consumer-pod-name>`.
>3. Allow Kubernetes to recreate the consumer.
>4. Check MySQL and MongoDB for continued insertion of data.
>5. Review logs and Prometheus metrics for signs of dropped or failed messages.
>
>**Expected Result:**  
>Consumer pod is automatically redeployed and resumes consuming messages from the correct offset without duplicate or lost data.

>#### Test Case: Sensor Pod Deletion Recovery  
>Verify that if a sensor pod is deleted, it will automatically restart and resume publishing data to Kafka.
>
>**Steps:**
>1. Deploy all services in Kubernetes, including a sensor pod (e.g., temperature).
>2. Monitor Prometheus metrics for active message publishing.
>3. Delete the sensor pod using `kubectl delete pod <sensor-pod-name>`.
>4. Wait for the pod to restart automatically.
>5. Observe Prometheus and Kafka logs to verify that message production resumes.
>
>**Expected Result:**  
>Sensor pod is recreated by Kubernetes and resumes normal operation without manual intervention. No lasting disruption to the Kafka message stream.


- **Pod scaling**: Scaled sensor producers up and down to evaluate system behavior under varied load. Confirmed that Kafka continued to handle message throughput and picked up where needed.

>#### Test Case: Pod Scaling Behavior  
>Confirm that scaling sensor or log-producer pods up or down does not disrupt message production or Kafka ingestion.
>**Steps:**
>1. Deploy the full system in Kubernetes, including Kafka and at least one sensor producer.
>2. Use the following command to scale the deployment up:  
>`kubectl scale deployment <producer-deployment-name> --replicas=3`
>3. Monitor Prometheus metrics and Kafka topic message rates to verify that message throughput increases appropriately.
>4. Then scale the deployment down:  
>`kubectl scale deployment <producer-deployment-name> --replicas=1`
>5. Observe that Kafka continues to ingest messages and no errors are reported in logs or metrics.
>
>**Expected Result:**  
>Kafka continues to receive and process messages without error. The system dynamically handles load changes as pods scale up or down. No dropped messages or crashes occur during scaling operations.

- **Database persistence**: Restarted and deleted both MongoDB and MySQL pods to validate persistent volume configuration. Ensured no data loss occurred and that stateful sets reattached storage volumes correctly on pod recreation.

>#### Test Case: Database Pod Persistence Validation  
>Confirm that MySQL and MongoDB retain data across pod restarts by validating persistent volume usage.
>
>**Steps:**
>1. Insert test data into both MySQL and MongoDB.
>2. Delete both database pods using `kubectl delete pod <db-pod-name>`.
>3. Allow Kubernetes to restart the pods.
>4. Query the databases to verify that all test data remains intact.
>
> **Example MySQL Queries**
> ```mysql
> select * from temperature_readings where value between "73" and "76";
> ```
> ```mysql
> select * from motion_readings where value like "1";
> ```
> ```mysql
> select * from humidity_readings where value between "40" and "56";
> ```
> **Example MongoDB Queries**
> ```mongo
> db.server_logs.find({ level: "INFO", component: "api" })
> ```
> ```mongo
> db.server_logs.find({ component: "frontend" })
> ```
> ```mongo
> db.server_logs.find({ level: "WARN", component: "frontend" })
> ```  
>**Expected Result:**  
>Both databases retain previously stored data after pod recreation, confirming correct persistent volume attachment and configuration.

### Observability Testing

- Confirmed that Prometheus was successfully scraping metrics from all producers and the consumer service.
- Verified accuracy of key metrics: message counts, error rates, sensor value gauges, and log severity breakdowns.
- Validated that Grafana dashboards updated in real-time and reflected accurate system status.

>#### Test Case: Observability Metrics Coverage  
>Validate that all relevant metrics are being exposed and scraped by Prometheus.
>
>**Steps:**
>1. Deploy all services and ensure Prometheus is running.
>2. Visit the Prometheus targets UI and confirm all endpoints are healthy.
>3. Trigger message production and log generation from producers.
>4. Check Prometheus and Grafana dashboards for:
>- Sensor value metrics
>- Message count and throughput
>- Log level metrics (INFO, WARNING, ERROR)
>- Processing success/failure rates
>
>**Expected Result:**  
>All expected metrics are available in Prometheus and visualized correctly in Grafana. No missing data points or unresponsive exporters.

### Testing Lessons Learned

While testing was largely exploratory and hands-on, it played a key role in surfacing potential edge cases and guiding improvements to fault tolerance. Given more time, we would have liked to incorporate automated test scripts and CI-integrated testing pipelines for more rigorous validation.

## Summary & Lessons Learned

Project: Arksense successfully demonstrated a scalable, resilient, and observable IoT simulation platform. By leveraging containerized microservices, Kubernetes orchestration, and a real-time Kafka-based data pipeline, our team was able to build a system that mirrored real-world production environments. Prometheus and Grafana added critical observability into system health, allowing us to test and visualize system behavior under dynamic conditions.

### Lessons Learned & Future Improvements

If given more time or resources, we would have liked to implement following enhancements to improve robustness, maintainability, and scalability:

- **Automated Testing Pipelines**  
  Introduce CI-integrated test workflows (e.g., GitHub Actions or GitLab CI) to validate deployments, Kafka functionality, and database connectivity after each change or PR. 

- **Kafka Consumer Group Scaling**  
  Implement multiple consumer replicas using Kafka consumer groups to allow for load balancing and better horizontal scalability.

- **Enhanced Security and Access Control**  
  Secure Kafka, Prometheus, and databases with role-based access control (RBAC), network policies, and secrets management via Kubernetes.   

This project laid a strong foundation in distributed system design and observability practices. It also highlighted the importance of site reliability engineering — not just building systems that work, but systems that recover gracefully and offer visibility into their state at all times.
