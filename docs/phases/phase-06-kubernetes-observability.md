# Phase 06 — Kubernetes, Helm, and Observability

## Objective

Package the API for K3s/Kubernetes with probes, resource controls, persistent storage,
Prometheus scraping, and a Grafana dashboard definition.

## Architecture

```text
Deployment -> Service -> ServiceMonitor -> Prometheus -> Grafana
     |            |
     v            v
    PVC        /metrics
```

## What was implemented

- Prometheus HTTP, job, frame, detection, and inference metrics.
- Helm Deployment, Service, ConfigMap, PVC, optional Ingress, ServiceMonitor, and dashboard.
- Non-root execution, liveness/readiness probes, and CPU/memory requests and limits.

## Original K3s commands

```bash
curl -sfL https://get.k3s.io | sh -
sudo kubectl get nodes
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
helm upgrade --install footballmatch ./helm/footballmatch-ai-platform -n footballmatch --create-namespace
kubectl get pods,svc,pvc -n footballmatch
```

K3s is lightweight Kubernetes. `helm upgrade --install` installs on first run and
upgrades later. These direct-install commands are retained as learning notes; the current
delivery target is Docker Desktop/WSL2 with k3d, so runtime evidence remains pending there.

## Validation

- 26 tests passed and Ruff passed.
- `helm lint` and `helm template` passed.
- K3s/Prometheus/Grafana runtime deployment is pending the local Docker Desktop/k3d host.

## Metrics

- `footballmatch_http_requests_total`
- `footballmatch_http_request_duration_seconds`
- `footballmatch_video_jobs_total`
- `footballmatch_frames_processed_total`
- `footballmatch_detections_total`
- `footballmatch_inference_duration_seconds`

## Limitations

- The local-path PVC is node-local and not highly available.
- In-memory jobs prevent safe multi-replica scaling; use one replica until durable state exists.
- Cluster dashboard evidence remains pending the local k3d deployment.

## How I would explain this phase in an interview

> Helm creates versioned Kubernetes releases. Probes distinguish restart health from
> traffic readiness; resource requests/limits make inference schedulable. Prometheus
> collects metrics and Grafana turns them into operational views.
