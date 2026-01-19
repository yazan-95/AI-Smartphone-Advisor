"""
vision3d.depth_estimator

Depth estimation using MiDaS (DPT Hybrid).
Optimized for macOS (MPS), CUDA, and CPU fallback.
"""

import torch
import numpy as np
from PIL import Image
from transformers import DPTForDepthEstimation, DPTImageProcessor


# -----------------------------
# SINGLETON MODEL LOAD
# -----------------------------
_DEVICE = (
    "mps"
    if torch.backends.mps.is_available()
    else "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

_PROCESSOR = DPTImageProcessor.from_pretrained("Intel/dpt-hybrid-midas")
_MODEL = DPTForDepthEstimation.from_pretrained("Intel/dpt-hybrid-midas").to(_DEVICE)
_MODEL.eval()


class DepthEstimator:
    """
    Thin wrapper around a singleton MiDaS depth model.
    """

    def estimate(self, image_path):
        """
        Estimate normalized depth map from image.

        Returns:
            np.ndarray of shape (H, W) normalized to [0, 1]
        """

        image = Image.open(image_path).convert("RGB")

        # Limit resolution for stability
        image.thumbnail((1024, 1024))

        inputs = _PROCESSOR(images=image, return_tensors="pt")
        inputs = {k: v.to(_DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            depth = _MODEL(**inputs).predicted_depth

        depth = depth.squeeze().cpu().numpy()

        # Normalize depth map
        depth_min = depth.min()
        depth_max = depth.max()

        if depth_max - depth_min < 1e-6:
            raise RuntimeError("Invalid depth map (flat values)")

        depth = (depth - depth_min) / (depth_max - depth_min)

        return depth
