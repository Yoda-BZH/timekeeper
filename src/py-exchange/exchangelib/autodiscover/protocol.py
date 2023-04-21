from ..protocol import BaseProtocol


class AutodiscoverProtocol(BaseProtocol):
    """Protocol which implements the bare essentials for autodiscover."""

    TIMEOUT = 10  # Seconds

    def __str__(self):
        return f"""\
Autodiscover endpoint: {self.service_endpoint}
Auth type: {self.auth_type}"""
