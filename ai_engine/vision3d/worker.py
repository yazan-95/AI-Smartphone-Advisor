"""
vision3d.worker

Runs heavy 3D jobs outside Django request lifecycle.
NEVER imports Django.
"""

from pathlib import Path


def generate_3d_phone(
    image_path: str,
    output_path: Path,
    model_name: str,
) -> None:
    """
    Background 3D generation job.

    - image_path: local filesystem path to phone image
    - output_path: final .glb output path
    - model_name: phone model name (for logging only)
    """

    try:
        from ai_engine.vision3d.phone_generator import generate_phone_glb_from_image

        generate_phone_glb_from_image(
            image_path=image_path,
            output_path=output_path,
            model_name=model_name,
        )

        if not output_path.exists():
            raise RuntimeError("3D generation finished but .glb not found")

    except Exception as e:
        print(f"[3D WORKER ERROR] {model_name}: {e}")
