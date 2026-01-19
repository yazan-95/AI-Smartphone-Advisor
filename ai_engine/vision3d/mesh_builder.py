"""
vision3d.mesh_builder

Converts a normalized depth map into a triangulated 3D mesh.
"""

import numpy as np
import trimesh


def depth_to_mesh(depth_map: np.ndarray, depth_scale: float = 1.0) -> trimesh.Trimesh:
    """
    Convert a depth map (H x W, normalized [0,1]) into a 3D mesh.

    Args:
        depth_map: np.ndarray (H, W)
        depth_scale: float, exaggerates depth for better 3D effect

    Returns:
        trimesh.Trimesh
    """

    if depth_map.ndim != 2:
        raise ValueError("Depth map must be 2D")

    h, w = depth_map.shape

    # Normalize XY to [-0.5, 0.5] for centered mesh
    xs = np.linspace(-0.5, 0.5, w)
    ys = np.linspace(-0.5, 0.5, h)
    xv, yv = np.meshgrid(xs, ys)

    zv = depth_map * depth_scale

    # Build vertices
    vertices = np.stack([xv, -yv, zv], axis=-1).reshape(-1, 3)

    # Build faces (two triangles per quad)
    faces = []
    for y in range(h - 1):
        for x in range(w - 1):
            i = y * w + x
            faces.append([i, i + 1, i + w])
            faces.append([i + 1, i + w + 1, i + w])

    faces = np.array(faces, dtype=np.int64)

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=True
    )

    mesh.remove_degenerate_faces()
    mesh.remove_duplicate_faces()
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()

    return mesh
