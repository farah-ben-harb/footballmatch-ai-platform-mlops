"""Prometheus metrics for API and computer-vision workload behaviour."""

from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "footballmatch_http_requests_total",
    "HTTP requests served by the FootballMatch API.",
    ("method", "path", "status_code"),
)
HTTP_DURATION = Histogram(
    "footballmatch_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "path"),
)
VIDEO_JOBS = Counter(
    "footballmatch_video_jobs_total",
    "Video analysis jobs by terminal or accepted state.",
    ("status",),
)
FRAMES_PROCESSED = Counter(
    "footballmatch_frames_processed_total",
    "Video frames processed by completed analysis jobs.",
)
DETECTIONS = Counter(
    "footballmatch_detections_total",
    "Object detections by COCO label.",
    ("label",),
)
INFERENCE_DURATION = Histogram(
    "footballmatch_inference_duration_seconds",
    "Total model inference duration of a video analysis job.",
)

VIDEO_ANALYSIS_DURATION = Histogram(
    "footballmatch_video_analysis_duration_seconds",
    "End-to-end duration of a video analysis job, including optional indexing.",
)
