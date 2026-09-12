# Concepts — Phase 04

## Model serving

### Definition

Model serving is making a trained or pretrained model available for inference through
a controlled interface, commonly an HTTP API.

### Why it exists

Users and other services should not need a Python shell, local model weights, or
knowledge of the CV framework to request analysis.

### How it works

FastAPI accepts a request, the application validates and persists input, a worker
executes the pipeline, and a separate endpoint exposes state and result.

### Architecture position

Between clients and the CV/MLflow workload.

### Alternatives

Batch CLI, synchronous HTTP inference, Celery/RQ workers, Kubernetes Jobs, or a
specialized serving system such as KServe. This local MVP uses FastAPI plus a thread.

### Advantages

Simple contract, small implementation, and an upgrade path toward durable workers.

### Limitations

An in-process thread is not fault-tolerant or scalable across replicas.

### Production considerations

Use authentication, object storage, durable jobs in PostgreSQL, a queue, retries,
idempotency keys, resource limits, and explicit retention.

### Security considerations

Validate actual media content and size; never trust filename or Content-Type alone.
Run untrusted video processing with restricted privileges.

### Common mistakes

- Keeping an HTTP connection open through a multi-minute inference.
- Loading model weights for every request.
- Using an in-memory job dictionary as a production database.

### Interview questions

Why return 202 rather than 200 from `POST /analyze`?

### Interview answers

202 means the server accepted work but has not completed it. It fits slow, asynchronous
video processing and lets clients poll a job resource.

## Batch versus online inference

### Definition

Batch inference processes a bounded collection offline or asynchronously. Online
inference returns a prediction during a request-response interaction.

### Why it exists

Different latency and throughput needs require different architectures.

### Example in our project

The API is asynchronous batch-style processing of an uploaded video; a per-frame
live-camera detection endpoint would be online inference.

### Alternatives

Streaming inference via RTSP/WebRTC, scheduled batch jobs, or event-driven workers.

### Production considerations

Match worker CPU/GPU sizing, queue depth, and timeout policy to the workload class.

### Interview questions

Why is this workload not a synchronous online API?

### Interview answers

Video duration makes inference unpredictable and potentially long. A synchronous
request would time out and consume web-server workers, so we return a job ID.

## Liveness versus readiness

### Definition

Liveness asks whether a process should be restarted; readiness asks whether it should
receive traffic.

### Example in our project

`/health` is a basic liveness signal and `/ready` reports the application ready.

### Production considerations

Kubernetes will later use these independently: a failed liveness check restarts a pod;
a failed readiness check removes it from service endpoints.

### Interview questions

What happens if readiness fails but liveness succeeds?

### Interview answers

The process stays running but receives no new traffic, allowing initialization or
dependency recovery without a restart loop.
