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
images for known CVEs. CI scans both the repository and the built image. The repository scan checks
source and dependency declarations; the image scan checks installed packages.

## CVEs and image scanning

### Definition

A CVE identifies a disclosed vulnerability. An image scanner inventories
installed packages and compares them to security advisories.

### Why it exists and architecture position

The release gate checks the actual API image before publication to GHCR.
Scanning source declarations alone misses base-image and transitive packages.

### Internal mechanism and alternatives

Trivy scans the built image, exits nonzero for fixable CRITICAL findings, and
blocks the dependent publish job. Requirements scanning is quicker but sees
less of the final artifact. Image scanning depends on advisory freshness and
does not prove the program is secure.

### Production and security considerations

Triage findings, upgrade fixed packages and compatible runtimes, rerun tests,
and rescan. Do not silence fixable critical findings just to pass CI.

### Interview question and answer

Why upgrade Python for a Pillow CVE? Pillow 13 requires Python 3.11+.
Python 3.10 would keep the resolver on an older vulnerable Pillow.

## MLflow migration and image identity

### Definition and internal mechanism

`mlflow db upgrade` runs Alembic migrations on a SQL backend. An OCI digest
is a content hash of an image manifest; a tag is a mutable registry name.

### Project workflow and architecture position

Backup PostgreSQL, stop writers, migrate, restart MLflow, and check old and
new runs. CI records the published digest; K3s can pin exactly that image.

### Alternatives and limitations

Discarding the database loses run history. Retaining vulnerable packages
leaves known issues. Digest pinning controls the image but does not protect
the stateful database; backup and recovery remain separate duties.

### Interview question and answer

Why is a commit-SHA tag not fully immutable? A registry can reassign the tag.
The digest names the actual content Kubernetes will pull.

### Commands to remember

`docker compose build mlflow`, `mlflow db upgrade <backend-store-url>`,
`docker compose up -d mlflow`, `git diff --staged`.

### Mental model

Source commit -> tests and scan -> published digest -> K3s deployment.
Database schema migrations have their own backup and validation path.
