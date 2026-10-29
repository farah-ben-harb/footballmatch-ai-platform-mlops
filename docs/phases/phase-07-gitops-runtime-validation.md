# Phase 07 Runtime Validation  Argo CD

## Objective

Validate pull-based GitOps on the single-node K3s VM while keeping the API runtime PVC and external PostgreSQL, MLflow, and Ollama services intact.

## Architecture

Git main -> Argo CD Core -> Helm render -> K3s Deployment, Service, ConfigMap, PVC

## Changes

- PR #23 merged the OCI digest support and GitOps Application.
- The Application targets `main`, uses Helm release name `footballmatch`, enables self-healing, and disables automatic prune to protect the PVC.
- The API image is pinned to `ghcr.io/farah-ben-harb/footballmatch-ai-platform-mlops@sha256:ec9c0d5d2130fc5f7e8353a9f87af43103d1cc1b069f9d59383b476bd889ae53`.
- Argo CD Core v3.5.6 was installed with the official core manifest.
- A minimal `default` AppProject was created for this repository and the `footballmatch` namespace.

## Validation commands

```bash
kubectl get pods -n argocd
kubectl get application footballmatch -n argocd
kubectl get deployment,pods,pvc -n footballmatch
kubectl describe application footballmatch -n argocd
```

## Evidence

- Argo CD components: application controller, applicationset controller, Redis, and repo server all `1/1 Running`.
- Argo CD Application: `Synced / Healthy` at revision `a78aa3b80367bc824bd3456afb720cedb016232f`.
- API Deployment: `1/1` available.
- Runtime PVC: `Bound`, 10 GiB, `local-path`.
- API `/health` and `/ready`: HTTP 200.
- Pod-to-MLflow health check: HTTP 200.
- Helm release: revision 6, status `deployed`.
- The image digest in the live Pod matches the CI publish digest.

## Failure and recovery

The first Helm upgrade timed out because an evicted old Pod remained in `Terminating` while the node was under ephemeral-storage pressure. K3s later cleared the disk-pressure taint after image cleanup. Removing only the failed/evicted Pod allowed the digest deployment to complete. The PVC was never deleted.

## Security and operations

- CI scans the image before publishing it.
- Kubernetes pulls by digest, avoiding tag reassignment ambiguity.
- GHCR credentials remain in `ghcr-pull`; database credentials remain in `footballmatch-rag-db`.
- Automatic prune is disabled because this chart owns persistent analysis artifacts.

## Interview explanation

CI produces and scans an immutable artifact. Argo CD pulls the reviewed Git desired state, renders Helm, compares live resources, and reconciles drift in the cluster. The deployment is pinned by OCI digest, while stateful data is protected by a persistent volume and a separate backup/migration process.

## Limitations and next step

Argo CD Core is headless and has no UI/API server in this small VM. Image promotion is a reviewed Git change. The next hardening step is a controlled rollback test using a previously published digest.