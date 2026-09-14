# Concepts — Phase 05

## Docker image, container, and Compose

### Definition

An image is an immutable filesystem/runtime template; a container is a running image
instance. Compose declares multiple containers, networks, volumes, and configuration.

### Why it exists

The API, MLflow, and PostgreSQL have different runtimes but must work together
repeatably on a developer machine.

### How it works

Compose creates a private DNS network; the API reaches MLflow as `http://mlflow:5000`
and MLflow reaches PostgreSQL as `postgres:5432`. Named volumes outlive containers.

### Alternatives

Manual commands are fragile; Kubernetes is more powerful but too heavy for local
single-host development. Compose is the bridge.

### Security considerations

Use non-root users, minimal base images, ignored `.env` files, and avoid baking
credentials into images.

### Interview questions

Image versus container? Volume versus bind mount?

### Interview answers

An image is the packaged blueprint; a container is its running instance. A named
volume is Docker-managed persistent data; a bind mount directly maps a host path.

## CI and DevSecOps

### Definition

Continuous integration automatically validates every change. DevSecOps integrates
security checks into that automated delivery flow.

### Why it exists

Manual review cannot reliably catch formatting regressions, broken tests, committed
secrets, insecure patterns, or vulnerable base images.

### How it works

GitHub Actions runs isolated jobs: Ruff/pytest, Gitleaks, Semgrep, image build, Trivy.

### Alternatives

GitLab CI, Jenkins, CircleCI, and hosted security platforms. GitHub Actions is free
for this repository workflow and sits beside pull requests.

### Interview questions

What do Gitleaks, Semgrep, and Trivy scan?

### Interview answers

Gitleaks detects likely credentials in Git history; Semgrep performs source-level
static analysis; Trivy scans dependencies, infrastructure configuration, and container
images for known CVEs. CI scans the repository because exporting the large local image
exceeds GitHub-runner disk; the Ubuntu release host scans the pushed image.
