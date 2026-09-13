# Concepts — Phase 03

## MLflow

### Definition

MLflow is an open-source system for tracking ML experiments, artifacts, and models.

### Why it exists

Without tracking, a metric such as “67 ball detections” has no reliable connection
to the model, threshold, data, or code that produced it.

### How it works

An experiment groups runs. A run stores immutable logged values: parameters describe
configuration, metrics describe numeric outcomes, tags add searchable context, and
artifacts store files. This MVP uses MLflow's local file store in `mlruns/`.

### Architecture position

It is the MLOps metadata layer beside the CV workload. Later it will use PostgreSQL
for metadata and shared artifact storage in container/Kubernetes environments.

### Example in our project

Each video run logs `model_name`, confidence, sampling rate, duration, detection
counts, summary JSON, and annotated MP4.

### Alternatives

Weights & Biases and Comet provide hosted tracking; custom database tables provide
control but require more implementation. MLflow is local, free, and includes a
future Model Registry path.

### Advantages

Comparable runs, auditability, artifact linkage, and no paid service requirement.

### Limitations

The local file store is not multi-user or production-safe by itself.

### Production considerations

Use a database backend, artifact store, access controls, retention policies, and
immutable model versions. Never rely only on a notebook or terminal log.

### Security considerations

Artifacts can expose source data or paths. Do not commit `mlruns/` or send sensitive
data to an untrusted tracking server.

### Common mistakes

- Calling MLflow a model.
- Logging metrics without the corresponding parameters/artifacts.
- Treating a file-store run as a production registry.

### Interview questions

What is an experiment, a run, an artifact, and a registered model?

### Interview answers

An experiment groups comparable work; a run is one execution; an artifact is a file
created or used by the run; a registered model is a managed, versioned model record
promoted for consumption. Tracking a run does not automatically register a model.

### Commands to remember

```powershell
.\.venv\Scripts\python.exe -m mlflow ui --backend-store-uri .\mlruns --port 5000
```

### Mental model / workflow

```text
configuration + data + model -> run -> metrics + artifacts -> comparison/promotion
```

## K-Means and jersey-colour features

### Definition

K-Means is an unsupervised algorithm that partitions numeric feature vectors into
`k` clusters by minimizing within-cluster squared distance (inertia).

### Why it exists

It lets us learn training-like ML lifecycle concepts without expensive labelled
datasets or GPU training. In this project, colour features from player crops can
later cluster two jerseys into probable teams.

### How it works

The algorithm selects centres, assigns each feature to its nearest centre, updates
centres to means, and repeats. `k=2` is the team-count hyperparameter; random state
makes initialization reproducible.

### Architecture position

Post-detection analytics layer: player crop -> colour feature -> K-Means -> team cluster.

### Alternatives

Manual colour thresholds are simpler but brittle. DBSCAN discovers cluster count but
is harder to tune. Supervised classification needs labelled examples.

### Advantages

Fast, explainable, local, and suitable for an MVP.

### Limitations

Clusters are not semantic labels: “cluster 0” is not intrinsically Team A. Lighting,
goalkeeper colours, referees, and crowd pixels can distort features.

### Interview questions

Why is K-Means unsupervised? What is inertia? Why make random state explicit?

### Interview answers

It uses no labelled target; inertia is within-cluster squared distance; random state
makes initialization and therefore results repeatable.
