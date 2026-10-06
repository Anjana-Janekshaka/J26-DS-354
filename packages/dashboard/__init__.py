"""Runtime dashboard: live strategy timeline, rationale, per-module panels and override control."""

from .render import render_static
from .server import serve

__all__ = ["render_static", "serve"]
