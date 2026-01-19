import os
from pathlib import Path
import trimesh

CACHE_DIR = Path(__file__).parent.parent / "static/recommender_app/models/3d_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def phone_model_path(model_name: str) -> Path:
    safe_name = model_name.replace(" ", "_").lower()
    return CACHE_DIR / f"{safe_name}.glb"

def generate_placeholder(model_name: str, specs: dict) -> str:
    path = phone_model_path(model_name)
    if path.exists():
        return str(path)

    width = specs.get("width_mm", 70)
    height = specs.get("height_mm", 150)
    thickness = specs.get("thickness_mm", 8)

    # Simple phone body
    box = trimesh.creation.box(extents=[width, thickness, height])

    # Simple camera bump
    cam_size = [15, 2, 15]
    cam_pos = [0, thickness/2 + cam_size[1]/2, height/2 - cam_size[2]/2]
    camera_bump = trimesh.creation.box(extents=cam_size)
    camera_bump.apply_translation(cam_pos)

    phone_mesh = trimesh.util.concatenate([box, camera_bump])
    phone_mesh.export(path)
    return str(path)
