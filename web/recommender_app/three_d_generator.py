"""
Django adapter for AI 3D generation pipeline

This file exists ONLY to bridge Django views
to ai_engine.three_d implementation.
"""

from ai_engine.vision3d.phone_generator import generate_phone_glb_from_image as _generate


def generate_phone_glb_from_image(image_path: str, output_name: str) -> str:
    """
    Wrapper used by Django views.

    Args:
        image_path: absolute path to input image
        output_name: output GLB filename

    Returns:
        relative static path to generated model
    """
    output_dir = "recommender_app/generated_models"
    return _generate(
        image_path=image_path,
        output_name=output_name,
        output_subdir=output_dir
    )
