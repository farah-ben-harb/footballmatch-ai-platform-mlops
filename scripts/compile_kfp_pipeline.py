"""Compile the FootballMatch Kubeflow Pipeline to IR YAML."""

from pathlib import Path

from kfp import compiler

from pipelines.footballmatch_pipeline import (
    footballmatch_pipeline,
)

OUTPUT_DIRECTORY = Path(
    "pipelines/compiled"
)

OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "footballmatch-ai-pipeline.yaml"
)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    compiler.Compiler().compile(
        pipeline_func=footballmatch_pipeline,
        package_path=str(
            OUTPUT_PATH
        ),
    )

    print(
        "Compiled Kubeflow pipeline:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()
