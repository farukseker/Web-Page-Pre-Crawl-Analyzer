from dataclasses import dataclass


@dataclass
class RobotTxtResult:
    content: str
    http_status: int
    has_err: bool
    render: None | str = None
