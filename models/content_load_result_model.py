from dataclasses import dataclass
import config


@dataclass
class ContentResultModel:
    processors: str
    title: str = ''
    content: str = ''
    raw_html: str = ''
    http_status: int = 0
    has_err: bool = False
    page_preview_path: str = config.DEFAULT_PREVIEW_IMAGE
    api_requests: set | None = None
    other_requests: set | None = None
