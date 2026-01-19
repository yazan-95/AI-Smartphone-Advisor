"""
vision3d.phone_generator

Responsible ONLY for generating a GLB from a local image.
NO Django imports.
NO networking.
"""

from pathlib import Path
from ai_engine.vision3d.depth_estimator import DepthEstimator
from ai_engine.vision3d.mesh_builder import depth_to_mesh


def generate_phone_glb_from_image(
    image_path: str,
    output_path: Path,
    model_name: str,
) -> None:
    """
    Generate a 3D GLB model from a phone image.

    - image_path: local filesystem path to input image
    - output_path: final .glb path (must be absolute)
    - model_name: used for logging only
    """

    image_path = Path(image_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1️⃣ Estimate depth
    estimator = DepthEstimator()
    depth_map = estimator.estimate(image_path)

    if depth_map is None:
        raise RuntimeError("Depth estimation failed")

    # 2️⃣ Build mesh
    mesh = depth_to_mesh(depth_map)

    if mesh is None:
        raise RuntimeError("Mesh generation failed")

    # 3️⃣ Export GLB
    mesh.export(output_path)

    if not output_path.exists():
        raise RuntimeError("GLB export failed")
