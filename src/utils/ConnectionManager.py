import secrets
from typing import Any, Dict, List, Protocol

from fastapi import WebSocket


class WebsocketManagerProtocol(Protocol):
    """Protocol for handling websocket connections."""

    active_games: Dict[str, WebSocket] = {}

    async def create_lobby(
        self, websocket: WebSocket, nickname: str, lobbyName: str
    ) -> str:
        """
        Create lobby with lobbyName.

        :param nickname: name of player who joins and also the leader
        :param lobbyName: the display name of the lobby
        create random token for lobby -> looking at active_games and find random token which does not exists
        create room with leader nickname in it
        join to that socket room (room = list of websockets)
        :returns: lobbyToken the token of the lobby that was created
        """
        ...

    async def join_room(
        self, websocket: WebSocket, nickname: str, lobbyToken: str
    ) -> str:
        """
        Join room with lobbyToken.

        :param nickname: name of player who joins
        :param lobbyToken: the lobby the player wants to joint
        search for lobby if it exitst
            -> if not return an error: {"message": "Lobby does not exists"}
        join this player to lobby with nickname
        :returns: lobbyName the name of the lobby joined
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

    async def create_lobby(
        self, websocket: WebSocket, nickname: str, lobbyName: str
    ) -> str:
        """
        Create lobby with lobbyName.

        :param nickname: name of player who joins and also the leader
        :param lobbyName: the display name of the lobby
        create random token for lobby -> looking at active_games and find random token which does not exists
        create room with leader nickname in it
        join to that socket room (room = list of websockets)
        :returns: lobbyToken the token of the lobby that was created
        """
        lobbyToken = secrets.token_urlsafe(12)

        for game in self.active_games.values():
            if game["lobby_name"] == lobbyName:
                raise NameError("Room name already exists")
            while True:
                if lobbyToken in self.active_games.keys():
                    lobbyToken = secrets.token_urlsafe(12)
                else:
                    break

        self.active_games[lobbyToken] = {
            "lobby_name": lobbyName,
            "connected": {nickname: websocket},
        }
        return lobbyToken

    async def send(self, websockets: List[WebSocket], data: Any):
        """Send data to one or more clients"""
        # TODO: Handle different data types
        if isinstance(data, Exception):  # TODO: This is a test
            for websocket in websockets:
                await websocket.send_json({"type": "error"})

    def disconnect(self, websocket: WebSocket) -> None:
        """Handle disconnection of a websocket."""
        ...
