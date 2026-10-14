"""
StickFilm AI Studio Pro - vidgen Core Engine
Package initialization
"""

try:
    from .voice_engine import VoiceEngine, VOICE_CATALOG
except ImportError:
    VoiceEngine = None
    VOICE_CATALOG = []

try:
    from .alignment_engine import AlignmentEngine
except ImportError:
    AlignmentEngine = None

try:
    from .prompt_engine import PromptEngine
except ImportError:
    PromptEngine = None

try:
    from .image_engine import ImageEngine
except ImportError:
    ImageEngine = None

try:
    from .video_renderer import VideoRenderer
except ImportError:
    VideoRenderer = None

try:
    from .thumbnail_engine import ThumbnailEngine
except ImportError:
    ThumbnailEngine = None

try:
    from .metadata_engine import MetadataEngine
except ImportError:
    MetadataEngine = None

try:
    from .pipeline import VideoPipeline
except ImportError:
    VideoPipeline = None

__all__ = [
    "VoiceEngine",
    "VOICE_CATALOG",
    "AlignmentEngine",
    "PromptEngine",
    "ImageEngine",
    "VideoRenderer",
    "ThumbnailEngine",
    "MetadataEngine",
    "VideoPipeline",
]

