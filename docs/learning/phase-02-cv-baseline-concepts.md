# Concepts — Phase 02

## Video, frames, FPS, and resolution

### Definition

A video is an encoded, timed sequence of image frames. FPS is its frame rate;
resolution is each frame's width and height.

### Why it exists

Computer-vision models consume images, so the video must be decoded into frames.

### How it works

OpenCV `VideoCapture` decodes sequential frames; `VideoWriter` encodes annotated
frames. Native handles must be released.

### Architecture position

Input/output layer around inference.

### Example in our project

The clip is 1920x1080 at about 30.36 FPS for 37.55 seconds.

### Alternatives

FFmpeg/PyAV offer finer codec control. OpenCV was chosen for a small local MVP.

### Advantages

Free, local, and direct integration with image operations.

### Limitations

Codec compatibility and non-integer FPS vary by environment.

### Production considerations

Validate duration, size, resolution, and codec before processing uploads.

### Security considerations

Treat malformed media as untrusted and run decoding with resource limits.

### Common mistakes

Loading every frame into memory or forgetting `release()`.

### Interview questions

What is the difference between a video and a frame?

### Interview answers

A frame is one image; a video is a timed, compressed sequence of frames.

### Commands to remember

```powershell
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 artifacts\annotated-match.mp4
```

### Mental model / workflow

```text
container -> decoder -> frames -> model -> encoder -> container
```

## Frame sampling

### Definition

Frame sampling processes a selected subset of video frames.

### Why it exists

Inference dominates CPU cost; sampling gives controllable throughput.

### How it works

`round(source_fps / target_fps)` produces an interval. Here 30.36/5 becomes 6,
so frames `0, 6, 12, ...` are processed.

### Architecture position

Between decoder and detector.

### Example in our project

190 frames were processed instead of all 1,140.

### Alternatives

Timestamp, scene-change, and adaptive sampling.

### Advantages

Deterministic, cheap, easy to test.

### Limitations

Brief events may occur between sampled frames.

### Production considerations

Log sampling rate as a versioned run parameter.

### Security considerations

Sampling does not replace a maximum video-duration limit.

### Common mistakes

Treating sampled detections as exhaustive evidence.

### Interview questions

Why sample frames?

### Interview answers

To reduce cost and latency, accepting reduced temporal detail.

### Commands to remember

```text
source FPS / target FPS -> interval
```

### Mental model / workflow

```text
all frames -> regular selection -> inference -> approximate timeline
```

## Object detection and YOLO

### Definition

Object detection predicts a class, confidence, and bounding box. IoU measures the
overlap of two boxes and helps remove duplicate candidates.

### Why it exists

Football analysis needs both what is present and where it is in a frame.

### How it works

YOLO produces boxes and class scores in one pass. `YoloDetector` converts those
vendor results into `Detection` objects and retains only `person` and `sports ball`.

### Architecture position

AI inference layer.

### Example in our project

The run observed 745 people and 67 sports-ball detections at a 0.25 threshold.

### Alternatives

Faster R-CNN, segmentation models, or a football-specific trained detector.

### Advantages

YOLO11n is small, local, free, and practical on CPU for the MVP.

### Limitations

COCO `person` cannot separate players, referees, and spectators; ball visibility is difficult.

### Production considerations

Track model identity, weights digest, threshold, hardware, and latency in MLflow.

### Security considerations

Model weights are third-party binaries: control source and provenance.

### Common mistakes

Calling per-frame counts unique players or treating confidence as certainty.

### Interview questions

What is IoU? Why can ball detection fail?

### Interview answers

IoU is overlap divided by total covered area. Balls are small, blurred, occluded,
and unlike many training examples.

### Commands to remember

```powershell
.\.venv\Scripts\python.exe scripts\analyze_video.py --input data\raw\match.mp4 --sample-fps 5 --confidence 0.25
```

### Mental model / workflow

```text
frame -> YOLO candidates -> filtering -> Detection objects -> annotation + metrics
```

## Training, inference, and adapters

### Definition

Training changes weights using data; inference applies fixed weights to new data.
An adapter hides a library behind an application contract.

### Why it exists

The seven-day MVP prioritises operating a model over costly custom detector training.

### How it works

The detector loads weights once, then exposes stable fields independent of Ultralytics tensors.

### Architecture position

Between model framework and application pipeline.

### Example in our project

Fake models make adapter tests deterministic without a network or GPU.

### Alternatives

Direct vendor calls everywhere, or a remote model-serving endpoint in Phase 4.

### Advantages

Faster tests and easier model replacement.

### Limitations

One small abstraction layer to maintain.

### Production considerations

Load models at startup, version them separately from serving code, and register them.

### Security considerations

Never deserialize untrusted weights; restrict artifact sources.

### Common mistakes

Loading a model for each frame/request or exposing framework tensors in an API.

### Interview questions

Why use a pretrained model and adapter?

### Interview answers

A pretrained model gives immediate baseline value; an adapter prevents vendor API
details spreading through the platform.

### Commands to remember

```text
yolo11n.pt + frame -> Detection
```

### Mental model / workflow

```text
vendor model -> adapter -> stable contract -> pipeline/API
```
