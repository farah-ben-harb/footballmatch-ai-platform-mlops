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
- GitOps deploy configuration uses immutable release tag `v0.1.0`, not `latest`.

## Commands to execute on Ubuntu

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f gitops/argocd/footballmatch-application.yaml
kubectl get applications -n argocd
kubectl get pods -n footballmatch
```

## Validation

- YAML manifests are committed and ready for an Argo CD-enabled K3s cluster.
- Runtime sync, drift repair, and rollback evidence are pending the Ubuntu VM.

## Security considerations

- The Argo Application uses a public read-only Git source; private repositories
  require a repository credential secret in Argo CD.
- GHCR publication uses the short-lived `GITHUB_TOKEN`, not a personal access token.
- Automatic prune is powerful: only enable it after confirming manifest ownership.

## Limitations

- The `v0.1.0` image must be published before Argo can deploy it.
- Image tag promotion is manually represented in Git; automated image update is deferred.
- Argo CD itself is not installed until the VM audit is complete.

## How I would explain this phase in an interview

> CI builds and validates an artifact. CD reconciles the running environment to a
> versioned declaration in Git. Argo CD is pull-based: the cluster controller pulls
> the desired state and detects drift, rather than GitHub Actions pushing kubectl
> commands with broad cluster credentials.
