from typing import Dict, Protocol

from fastapi import WebSocket


class WebsocketManagerProtocol(Protocol):
    """Protocol for handling websocket connections."""

    active_games: Dict[str, WebSocket] = {}

    def __init__(self) -> None:  # noqa: D102
        ...

    async def create_lobby(self, websocket: WebSocket, nickname: str, lobbyName: str) -> str:
        """
        Create lobby with lobbyName.

        DataComesIn: {nickname: string, lobbyName: string} -> nickname will be the leader of the lobby
        create random token for lobby -> looking at active_games and find random token which does not exists
        create room with leader nickname in it
        join to that socket room (room = list of websockets)
        DataGoesOut: {token: string} -> this will be the token of the lobby
        """
        ...

    async def join_room(self, websocket: WebSocket, nickname: str, lobbyToken: str) -> str:
        """
        Join room with lobbyToken.

        DataComesIn: {nickname: string, lobbyToken: string}
        search for lobby if it exitst
            -> if not return an error: {"message": "Lobby does not exists"}
        join this player to lobby with nickname
        DataGoesOut: {lobbyName: str}
        """
        ...

    async def receive(websocket: WebSocket) -> None:
        """Receive websocket data and transfer it to the correct function."""
        ...

    async def send(websocket: list[WebSocket], type: str, data: Dict):
        """
        Send data to the specified websockets.

        :param websocket: list of websockets to send data to
        :param type: type of data to send (i.e. "create_lobby")
        :param data: data to send
        """
        ...

    async def disconnect(self, websocket: WebSocket) -> None:
        """Handle disconnection of a websocket."""
        ...


class WebsocketManager:
    """Handles websocket connections."""

    def __init__(self):
        self.active_games: Dict[str, WebSocket] = {}
