from __future__ import annotations

__all__ = ["maybe_init_ray"]


def maybe_init_ray(para_check: int, ray_dir: str) -> bool:
    """Initialize Ray if requested; return True if initialized."""
    if para_check > 1 and ray_dir != '':
        import ray
        ray.init(_temp_dir=ray_dir, num_cpus=para_check)
        return True
    return False
