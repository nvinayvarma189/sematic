try:
    import torch  # noqa: F401
except ImportError:
    pass
else:
    import glow.types.types.pytorch.dataloader  # noqa: F401