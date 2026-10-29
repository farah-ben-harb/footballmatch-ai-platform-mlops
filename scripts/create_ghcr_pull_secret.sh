#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 3 ]]; then
  echo "Usage: token-producer | $0 NAMESPACE SECRET_NAME GITHUB_USER" >&2
  exit 2
fi

namespace="$1"
secret_name="$2"
github_user="$3"
registry_token="$(tr -d '\r\n')"

if [[ -z "$registry_token" ]]; then
  echo "No registry token received on stdin." >&2
  exit 1
fi

registry_auth="$(printf '%s:%s' "$github_user" "$registry_token" | base64 | tr -d '\r\n')"
unset registry_token

kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -

printf '{"auths":{"ghcr.io":{"auth":"%s"}}}' "$registry_auth" |
  kubectl -n "$namespace" create secret generic "$secret_name" \
    --from-file=.dockerconfigjson=/dev/stdin \
    --type=kubernetes.io/dockerconfigjson \
    --dry-run=client -o yaml |
  kubectl apply -f -

unset registry_auth
