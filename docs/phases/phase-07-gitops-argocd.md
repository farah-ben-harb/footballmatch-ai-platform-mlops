# Phase 07 — GitOps and Argo CD

## Objective

Use Git as the desired-state source for a Kubernetes release and configure Argo CD to
continuously reconcile the cluster with that source.

## Architecture

```text
Git main -> Argo CD Application -> Helm render -> K3s desired state
                   ^                                  |
                   |---------- drift detection --------|
```

## What was implemented

- An Argo CD `Application` targeting this repository’s Helm chart on `main`.
- Automated sync, prune, self-healing, and namespace creation.
- A CI publish job that publishes verified `main` images to free GitHub Container
  Registry (GHCR) after test, secret, SAST, and Trivy jobs succeed.
- GitOps deploy configuration pins the CI-published commit-SHA image tag, not `latest`.

## Commands to execute on the local k3d cluster

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f gitops/argocd/footballmatch-application.yaml
kubectl get applications -n argocd
kubectl get pods -n footballmatch
```

## Validation

- YAML manifests are committed and ready for an Argo CD-enabled K3s cluster.
- Runtime sync, drift repair, and rollback evidence are pending the local Docker Desktop/k3d host.

## Security considerations

- The Argo Application uses a public read-only Git source; private repositories
  require a repository credential secret in Argo CD.
- GHCR publication uses the short-lived `GITHUB_TOKEN`, not a personal access token.
- Automatic prune is powerful: only enable it after confirming manifest ownership.

## Limitations

- The manifest pins a CI-published commit-SHA image; a future release will promote it to `v0.1.0`.
- Image tag promotion is manually represented in Git; automated image update is deferred.
- Argo CD itself is not installed until the local host audit is complete.

## How I would explain this phase in an interview

> CI builds and validates an artifact. CD reconciles the running environment to a
> versioned declaration in Git. Argo CD is pull-based: the cluster controller pulls
> the desired state and detects drift, rather than GitHub Actions pushing kubectl
> commands with broad cluster credentials.
