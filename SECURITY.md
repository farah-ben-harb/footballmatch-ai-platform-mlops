# Security Policy

## Local development rules

- Never commit `.env`, videos, model weights, MLflow artifacts, database volumes, or credentials.
- Use only media you are permitted to process and share.
- Replace the PostgreSQL password placeholder before starting Compose.
- Keep API binding local unless authentication, TLS, and network controls are configured.

## Reporting

Do not open a public issue containing a secret. Rotate the exposed value immediately,
remove it from Git history where necessary, then report the impact privately to the
repository owner.

## Security controls in this repository

- Gitleaks scans Git history for likely secrets.
- Semgrep scans Python source for risky patterns.
- Trivy blocks high/critical dependency and infrastructure-as-code findings in CI.
  A full pushed-image scan is a release-environment check on the local deployment host
  because exporting the local YOLO/PyTorch image can exceed a GitHub runner's ephemeral disk.
- Containers use a non-root runtime user.
- Uploads use an extension allow-list and size limit; content validation and malware
  scanning remain future work.
