"""Run the local football-video analysis baseline from the command line."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from footballmatch_api.cv.detector import YoloDetector
from footballmatch_api.cv.pipeline import analyze_video


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a football match video with YOLO.")
    parser.add_argument("--input", type=Path, required=True, help="Path to an input video file.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/annotated-match.mp4"),
        help="Path for the annotated MP4 output.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("artifacts/analysis-summary.json"),
        help="Path for the JSON run summary.",
    )
    parser.add_argument("--sample-fps", type=float, default=5.0, help="Frames per second to analyze.")
    parser.add_argument("--confidence", type=float, default=0.25, help="YOLO confidence threshold.")
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    detector = YoloDetector(confidence_threshold=arguments.confidence)
    summary = analyze_video(
        input_path=arguments.input,
        output_path=arguments.output,
        detector=detector,
        target_fps=arguments.sample_fps,
    )
    arguments.summary.parent.mkdir(parents=True, exist_ok=True)
    arguments.summary.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
    print(json.dumps(asdict(summary), indent=2))


if __name__ == "__main__":
    main()
