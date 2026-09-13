# Concepts — Phase 07

## GitOps and reconciliation

### Definition

GitOps stores desired infrastructure/application state in Git and uses a controller to
reconcile actual cluster state to it.

### Why it exists

It makes deployment reviewable, auditable, reproducible, and recoverable through Git.

### How it works

Argo CD watches the Application source, renders Helm, compares live resources, then
syncs differences. A manual `kubectl` change becomes drift and self-heal can revert it.

### Alternatives

Push deployment from CI, Flux CD, or manual kubectl. Argo CD provides UI, comparison,
health, history, and a pull-based model.

### Interview questions

CI versus CD? Push versus pull deployment? Helm versus Argo CD?

### Interview answers

CI validates/builds artifacts; CD makes approved desired state run. Push CI holds
cluster credentials and sends changes; pull controllers run in-cluster and fetch Git.
Helm templates resources; Argo CD decides when/if they are reconciled.
