class LobbyException(Exception):
    """Join/create lobby exception"""

    action: str
    field: str
    message: str

    def __init__(self, action: str, field: str, message: str, *args: object) -> None:
        super().__init__(field, message, *args)
        self.action = action
        self.field = field
        self.message = message

    def __str__(self) -> str:
        return super().__str__()

    def as_json(self) -> dict:
        """Return data as dict, to send via websocket"""
        return {"type": self.action, "error": {self.field: self.message}}
