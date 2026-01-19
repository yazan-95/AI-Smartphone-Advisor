"""
vision3d.pipeline.py

High-level orchestration for 3D phone generation.
SAFE for Django imports.
Cache-aware and idempotent.
"""

import threading
from pathlib import Path
from django.conf import settings

def generate_phone_3d_model(model_name: str, save_path: str):
    """
    Generates a 3D .glb model from 2D rendering.
    This is a placeholder example; integrate your 2D→3D engine here.
    """
    import trimesh
    import pyrender

    # STEP 1: Generate a simple box representing phone dimensions
    width, height, depth = 0.07, 0.15, 0.008  # meters, example dimensions
    mesh = trimesh.creation.box(extents=[width, height, depth])

    # STEP 2: Export to .glb
    mesh.export(save_path)

def run_3d_job(image_path: str, model_name: str) -> None:
    """
    Fire-and-forget background job.
    Safe to call from Django views.

    - image_path: local filesystem path (NOT URL)
    - model_name: phone model name
    """

    model_safe = model_name.lower().replace(" ", "_")
    output_glb = Path(settings.MEDIA_ROOT) / "3d_models" / f"{model_safe}.glb"

    # ✅ HARD STOP if already generated
    if output_glb.exists():
        return

    def _job():
        try:
            from ai_engine.vision3d.worker import generate_3d_phone
            generate_3d_phone(
                image_path=image_path,
                output_path=output_glb,
                model_name=model_name,
            )
        except Exception as e:
            # Never crash Django thread
            print(f"[3D PIPELINE ERROR] {model_name}: {e}")

    thread = threading.Thread(target=_job, daemon=True)
    thread.start()
