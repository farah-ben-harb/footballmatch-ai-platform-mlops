# Computer vision and MLOps integration validation

Validated locally on 2026-11-08 with Python 3.12.16, MLflow 3.17.2,
Ultralytics 8.4.207, and `lap` 0.5.14. The integration branch starts from
`main` at `536478c` and brings the reproducibility, ByteTrack, team-clustering,
and model-registry commits into the current application.

## Automated checks

- `python -m pytest -q`: 55 tests passed.
- `python -m ruff check .`: passed.
- The local video and MLflow registry checks below used real model weights and inputs.

## Real video smoke test

Input: a local five-second football clip, 854 x 480 pixels at 15 FPS. Processing
at 3 FPS produced 15 annotated frames, 64 person detections, one sports-ball
detection, 22 unique person track IDs, and one sports-ball track ID. Twelve
person tracks had enough jersey samples for clustering: eight in `team_0` and
four in `team_1`. Classification coverage was 0.545 and the silhouette score
was 0.610. The local MLflow run ID was
`e776a5e1ac9149bea6604b163fa75417`.

The annotated MP4, JSON summary, and MLflow SQLite database were created under
ignored local directories. The clip has no curated ground-truth boxes or
identity/team labels. Detection precision/recall, track ID accuracy, and team
classification accuracy therefore remain unmeasured. The 22 person track IDs
must not be interpreted as 22 distinct players.

## Model Registry smoke test

The YOLO checkpoint was registered in a local SQLite-backed MLflow Model
Registry as version 2. An image from the clip produced seven person detections
through the registered `candidate` model. The smoke test tagged that version,
and the promotion script assigned it the `champion` alias. The same video was
then analyzed through `models:/FootballMatchYOLODetector@champion` and produced
the same frame and detection counts, plus MLflow run
`90fe7bcad91c4f47b98e08be339de6c5`.

A FastAPI `POST /analyze` request using the same local clip and champion URI
returned a job ID. Polling `GET /jobs/{id}` reached `completed`, and
`GET /matches/{id}` returned HTTP 200 with 15 processed frames and MLflow run
`bf5558b21e894db2afd11f47de3b0940`.

The smoke gate proves the model can be loaded and run. It is not a model-quality
gate. Promotion to a deployment used for decisions still requires a labelled
benchmark and review of precision, recall, identity switches, and team labels.
No production or Azure deployment was changed by these local tests.
