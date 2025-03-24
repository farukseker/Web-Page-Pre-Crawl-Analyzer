from dataclasses import dataclass


@dataclass
class RobotTxtResult:
    processor: str
    content: str = ''
    http_status: int = 0
    has_err: bool = False
    render: None | str = None
