# Concepts — Phase 06

## Kubernetes and Helm

### Definition

Kubernetes schedules containers as Pods. A Deployment maintains replicas, a Service
provides stable networking, and a PVC requests persistent storage. Helm packages and
templates those resources.

### Why it exists

Containers alone do not provide scheduling, desired state, service discovery, or
declarative upgrades.

### Architecture position

K3s hosts the workload; Helm renders application configuration.

### Alternatives

Compose is suitable for one host; raw YAML has less reuse; managed Kubernetes costs money.

### Interview questions

Deployment versus Pod? ConfigMap versus Secret? Liveness versus readiness?

### Interview answers

A Pod runs containers; a Deployment maintains desired Pods. ConfigMaps hold non-secret
configuration; Secrets hold sensitive values. Liveness can restart a process; readiness
removes an unready process from traffic.

## Prometheus and Grafana

### Definition

Prometheus pulls labelled numeric series from `/metrics`; Grafana queries and visualizes them.

### Why it exists

Metrics reveal traffic, latency, errors, and capacity trends across time, unlike isolated logs.

### How it works

A ServiceMonitor selects an endpoint for Prometheus. The dashboard uses rates and
histograms to show throughput, job outcomes, detections, and p95 inference time.

### Interview questions

Why metrics and not only logs? What is a histogram?

### Interview answers

Metrics allow aggregation and alerting. A histogram counts observations in buckets,
which allows percentile estimates such as p95 latency.
