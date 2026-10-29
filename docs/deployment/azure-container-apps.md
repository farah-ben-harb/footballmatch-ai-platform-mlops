# Azure Container Apps deployment evidence

## Scope

This document records a reproducible, read-only validation of the public Azure
Container App used for the portfolio demo. It is evidence for the deployed API,
not a claim that every Kubernetes and GitOps manifest in this repository is live in
Azure.

## Deployment identity

| Field | Verified value |
| --- | --- |
| Resource group | `footballmatch-demo-rg` |
| Region | `francecentral` |
| Container App | `footballmatch-api-demo2` |
| Environment | `footballmatch-demo-env` |
| Public URL | `https://footballmatch-api-demo2.nicewater-00626e15.francecentral.azurecontainerapps.io` |
| Image | `ghcr.io/farah-ben-harb/footballmatch-ai-platform-mlops:sha-465b6d90c19bbe8f108375efb0bab452d4919226` |
| Runtime sizing | 1 vCPU, 2 GiB |
| Scaling | `minReplicas=0`, `maxReplicas=1` |

## Health and readiness validation

PowerShell commands used:

```powershell
$base = "https://footballmatch-api-demo2.nicewater-00626e15.francecentral.azurecontainerapps.io"

[pscustomobject]@{
    Health = (Invoke-RestMethod "$base/health").status
    Ready  = (Invoke-RestMethod "$base/ready").status
    RAG    = (Invoke-RestMethod "$base/rag/status").status
    Docs   = (Invoke-WebRequest "$base/docs").StatusCode
    Metrics = (Invoke-WebRequest "$base/metrics").StatusCode
}
```

Observed result:

```text
Health  Ready  RAG         Docs  Metrics
------  -----  ---         ----  -------
ok      ready  configured  200   200
```

The root path `/` is intentionally not an application route, so opening the bare
hostname returns FastAPI's normal `{"detail":"Not Found"}` response. Use `/docs`
for the interactive API interface.

## End-to-end video analysis

The input was the short Wikimedia Commons football clip documented in the README.
The API call used `sample_fps=5` and `confidence_threshold=0.25`.

Observed completed job:

| Field | Value |
| --- | --- |
| Job ID | `ba8e127a-ab8b-4e9f-90f1-a03dbc7ba32b` |
| Status | `completed` |
| Model | `yolo11n.pt` |
| Source/effective FPS | `25 / 5` |
| Frames processed | `44` |
| `person` detections | `318` |
| `sports ball` detections | `63` |
| Inference duration | `2.2763 s` |
| Total duration | `4.4791 s` |
| MLflow run | `630ad32554a2462c89a637b31f672cb7` |

The service returned HTTP `202` for `POST /analyze`, followed by `completed` from
`GET /jobs/{id}` and the same result from `GET /matches/{id}`.

## Observability evidence

The Prometheus endpoint exposed application metrics after the run, including:

- completed video jobs;
- processed frames;
- detections by COCO label;
- inference duration;
- end-to-end analysis duration;
- HTTP request counters and latency histograms.

The RAG counters remained at zero because PostgreSQL/pgvector and Ollama are not
configured in this Azure demo.

## Cost and security posture

- The app is configured for scale-to-zero (`minReplicas=0`) when idle.
- No credentials or registry tokens are stored in this repository.
- The image is referenced by an immutable commit SHA rather than `latest`.
- The demo backend uses ephemeral container storage and SQLite for MLflow metadata.
- Production use would require durable storage, authentication, TLS controls,
  queue-backed workers, and a managed database with backups.

## Reproduction checklist

```powershell
$base = "https://footballmatch-api-demo2.nicewater-00626e15.francecentral.azurecontainerapps.io"
Invoke-RestMethod "$base/health"
Invoke-RestMethod "$base/ready"
Invoke-WebRequest "$base/docs" | Select-Object StatusCode
Invoke-WebRequest "$base/metrics" | Select-Object StatusCode

az containerapp show `
  --name footballmatch-api-demo2 `
  --resource-group footballmatch-demo-rg `
  --query "{state:properties.provisioningState,running:properties.runningStatus,minReplicas:properties.template.scale.minReplicas,maxReplicas:properties.template.scale.maxReplicas}" `
  -o table
```

Expected final scaling configuration is `Succeeded`, `minReplicas=0`, and
`maxReplicas=1`.
