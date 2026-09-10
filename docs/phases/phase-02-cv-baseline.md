# Phase 02 — Computer Vision Baseline

## Objective

Create a local, CPU-friendly football-video inference baseline with observable output and metrics.

## Starting state

- Phase 1 FastAPI foundation was merged to `main`.
- Windows Python 3.10 virtual environment and FFmpeg were available.
- Docker validation and Ubuntu VM audit remain pending.

## Architecture

```text
match.mp4 -> OpenCV metadata -> 5 FPS sampling -> YOLO11n CPU
          -> person/sports ball detections -> annotated MP4 + JSON summary
```

## What was implemented

- OpenCV and Ultralytics dependencies.
- Video metadata validation, sampling plan, and streaming frame iteration.
- A `YoloDetector` adapter that produces application-owned `Detection` objects.
- A pipeline that annotates frames and writes an MP4 output.
- A CLI at `scripts/analyze_video.py`.
- Unit tests using fake video, model, and writer collaborators.
- Git ignore rules for data, artifacts, and `.pt` weights.

## Files added or modified

`.gitignore`, `pyproject.toml`, `README.md`, `src/footballmatch_api/cv/`,
`scripts/analyze_video.py`, and `tests/test_video.py`, `tests/test_detector.py`,
`tests/test_pipeline.py`.

## Commands executed

### Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Installs the project in editable mode (`-e`) and its declared dependencies.

### Run checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

`pytest` verifies behaviour; Ruff finds Python style and correctness issues.

### Process the video

```powershell
.\.venv\Scripts\python.exe scripts\analyze_video.py --input data\raw\match.mp4 --output artifacts\annotated-match.mp4 --summary artifacts\analysis-summary.json --sample-fps 5 --confidence 0.25
```

`--sample-fps` controls compute cost; `--confidence` filters weak predictions.

### Validate output

```powershell
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 artifacts\annotated-match.mp4
```

FFprobe reads output metadata without fully decoding the video.

## Validation

- 16 tests passed.
- Ruff and `git diff --check` passed.
- FFprobe confirmed the annotated MP4 is readable.

## Tests executed

```text
16 passed
All checks passed
```

## Evidence

```text
Input: 1920x1080, 30.3587 FPS, 1,140 frames, 37.551 s
Model: yolo11n.pt
Frames processed: 190
Effective FPS: 5.0598
Person detections: 745
Sports-ball detections: 67
Inference time: 32.76 s
Total time: 50.85 s
Output: 1920x1080, 37.55 s, MPEG-4 stream
```

## Errors encountered

- A placeholder source path was copied literally and did not exist.
- FFprobe was run before FFmpeg completed, producing `moov atom not found`.
- Early fake-test type annotations and import ordering failed lint/test collection.

## Root causes

Placeholders are not real paths; MP4 metadata is finalised at encoding completion;
Python 3.10 evaluates an invalid `float | "Type"` union expression at runtime.

## Fixes

Used a licensed local input, waited for FFmpeg completion, simplified the annotation,
and applied Ruff's safe import formatting.

## Security considerations

- Media, artifacts, and model weights are ignored by Git.
- Future upload APIs must validate media size, codec, duration, and content.
- The source clip is [This is soccer on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:This_is_soccer.webm), CC BY-SA 3.0; attribution must accompany shared derivatives.

## DevOps / MLOps best practices applied

- Reproducible dependency declaration.
- Streaming memory use.
- Stable adapter boundary around a vendor model.
- Tests that avoid costly model downloads.
- Measured run output captured as a JSON artifact.

## Git / PR summary

Branch: `feat/cv-baseline`.

Suggested PR title: `feat(cv): add sampled football video analysis baseline`

Suggested commits:

- `feat(cv): add sampled YOLO video analysis baseline`
- `test(cv): cover video detector and pipeline helpers`
- `docs(phase-02): document computer vision baseline`

## Limitations

- `person` includes players, referees, and possible spectators.
- Ball detections can fail due to blur, size, and occlusion.
- Counts are observations per frame, not unique tracked objects.
- Output audio is omitted.
- CPU throughput is suitable for this short MVP video, not high-volume production.

## Next phase

Phase 3 adds a small ML component and MLflow tracking for parameters, metrics,
artifacts, and model metadata.

## How I would explain this phase in an interview

> I built a CPU-first YOLO inference pipeline that validates media, samples frames,
> converts raw framework outputs into stable application objects, streams annotated
> video to disk, and records latency and detection metrics. I deliberately document
> that COCO `person` is not a referee/player classifier.
