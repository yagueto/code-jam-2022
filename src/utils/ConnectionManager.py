from secrets import token_urlsafe
from typing import Any, Dict, List, Protocol

from fastapi import WebSocket

from utils.Exceptions import LobbyException


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
        self.active_connections: Dict[WebSocket, str] = {}
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
        lobbyToken = token_urlsafe(12)

        for game in self.active_games.values():
            if game["lobby_name"] == lobbyName:
                raise LobbyException(
                    action="create_lobby", field="lobby_name", message="already exists"
                )
            while True:
                if lobbyToken in self.active_games.keys():
                    lobbyToken = token_urlsafe(12)
                else:
                    break

        self.active_games[lobbyToken] = {
            "lobby_name": lobbyName,
            "connected": {websocket: nickname},
        }
        return lobbyToken

    async def join_lobby(self, websocket: WebSocket, nickname: str, lobbyToken: str):
        """Join already existing lobby"""
        if lobbyToken in self.active_games:
            self.active_games[lobbyToken]["connected"][websocket] = nickname
            self.active_connections[websocket] = lobbyToken
        else:
            await self.send(websockets=[websocket], data="Lobby does not exist")

    async def connect(self, websocket: WebSocket):
        """Accept connection and add it to list of active connections"""
        await websocket.accept()
        self.active_connections[websocket] = None

    async def receive(self, websocket: WebSocket):
        """Receive data from websocket and process it"""
        data: dict = await websocket.receive_json()
        try:
            match data["type"]:
                case "create_lobby":
                    lobbyToken = await self.create_lobby(
                        websocket, data["data"]["nickname"], data["data"]["lobby_name"]
                    )
                    print(f"{websocket.client} - assigned to room")
                    self.active_connections[websocket] = lobbyToken
                    await websocket.send_json(
                        {
                            "type": "create_lobby",
                            "data": {"lobby_token": lobbyToken},
                        }
                    )
                    return
                case "join_lobby":
                    for game in self.active_games:
                        if (
                            self.active_games[game]["lobby_name"]
                            == data["data"]["lobby_name"]
                        ):
                            for user in self.active_games[game]["connected"].values():
                                if user == data["data"]["nickname"]:
                                    raise LobbyException(
                                        action="join_lobby",
                                        field="nickname",
                                        message="already exists",
                                    )
                            await self.join_lobby(
                                websocket=websocket,
                                nickname=data["data"]["nickname"],
                                lobbyToken=game,
                            )
                            self.active_connections[websocket] = game

                            await self.send(
                                websockets=[websocket],
                                data={
                                    "type": "join_lobby",
                                    "data": {"lobby_token": game},
                                },
                            )
                            return
                    await self.send(websockets=[websocket], data="Room not found")
                case _:
                    await self.send(
                        websockets=[websocket], data="Unimplemented/Bad request"
                    )
        except KeyError as e:
            action = data.get("type", None)
            await self.send(websockets=[websocket], data={
                "type": action,
                "error": {
                    "Missing key": e.args[0]
                }
            })

        except LobbyException as e:
            await self.send(websockets=[websocket], data=e.as_json())

    async def send(self, websockets: List[WebSocket], data: Any):
        """Send data to one or more clients"""
        # TODO: Handle different data types
        if isinstance(data, Exception):  # TODO: This is a test
            for websocket in websockets:
                await websocket.send_json({"type": "error", "data": data.args})
        elif type(data) is dict:
            for websocket in websockets:
                await websocket.send_json(data)
        else:
            for websocket in websockets:
                await websocket.send_json({"message": data})

    def disconnect(self, websocket: WebSocket, lobbyToken) -> None:
        """Handle disconnection of a websocket."""
        print(f"{websocket.client} has disconnected - removing.")
        lobbyToken = self.active_connections[websocket]
        if lobbyToken:
            del self.active_games[lobbyToken]["connected"][websocket]
            print(f"{websocket.client} was in room {lobbyToken} - removing from room")
            if len(self.active_games[lobbyToken]["connected"]) == 0:
                del self.active_games[lobbyToken]
                print("Room is empty - closing")

        del self.active_connections[websocket]
