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

Testing for Project: Arksense focused primarily on validating system resilience, reliability, and core functional correctness within a Kubernetes-managed environment. While formal test cases and automation were limited, a variety of manual and scenario-based tests were conducted throughout development to ensure system behavior aligned with expectations.

### Functional Testing

- Verified that all sensor and log producer services successfully published data to Kafka topics.
- Confirmed that the Kafka consumer correctly parsed messages and routed them to either MySQL or MongoDB based on data type.
- Tested database insertions to ensure correct data formatting, schema adherence (MySQL), and document structure (MongoDB).

### Resilience & Recovery Testing

- **Pod deletion and restart**: Manually deleted various pods (sensors, consumer, databases) to observe Kubernetes auto-recovery. Verified that functionality resumed without manual intervention and that message flow remained intact.
- **Pod scaling**: Scaled sensor producers  up and down to evaluate system behavior under varied load. Confirmed that Kafka continued to handle message throughput and picked up where needed.
- **Database persistence**: Restarted and deleted both MongoDB and MySQL pods to validate persistent volume configuration. Ensured no data loss occurred and that stateful sets reattached storage volumes correctly on pod recreation.

### Observability Testing

- Confirmed that Prometheus was successfully scraping metrics from all producers and the consumer service.
- Verified accuracy of key metrics: message counts, error rates, sensor value gauges, and log severity breakdowns.
- Validated that Grafana dashboards updated in real-time and reflected accurate system status.

### Lessons Learned

While testing was largely exploratory and hands-on, it played a key role in surfacing potential edge cases and guiding improvements to fault tolerance. Given more time, we would have liked to incorporate automated test scripts and CI-integrated testing pipelines for more rigorous validation.
