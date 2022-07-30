from secrets import token_urlsafe
from typing import Any, Dict, List, Protocol

from fastapi import WebSocket

from Game import Game
from utils.Exceptions import LobbyException


class WebsocketManagerProtocol(Protocol):
    """Protocol for handling websocket connections."""

    active_games: Dict[str, WebSocket] = {}

    async def create_lobby(self, websocket: WebSocket, nickname: str, lobbyName: str) -> str:
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

    async def join_room(self, websocket: WebSocket, nickname: str, lobbyToken: str) -> str:
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

    async def create_lobby(self, websocket: WebSocket, nickname: str, lobbyName: str) -> str:
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
                raise LobbyException(action="create_lobby", field="lobby_name", message="already exists")
            while True:
                if lobbyToken in self.active_games.keys():
                    lobbyToken = token_urlsafe(12)
                else:
                    break

        self.active_games[lobbyToken] = {
            "lobby_name": lobbyName,
            "game": None,
            "connected": {websocket: nickname},
            "status": {},
        }
        return lobbyToken

    async def join_lobby(self, websocket: WebSocket, nickname: str, lobbyToken: str):
        """Join already existing lobby"""
        self.active_games[lobbyToken]["connected"][websocket] = nickname
        self.active_connections[websocket] = lobbyToken
        event = {"type": "join_lobby", "data": {nickname: "joined"}}
        await self.send(websockets=self.active_games[lobbyToken]["connected"].keys(), data=event)

    async def leave_lobby(self, websocket: WebSocket):
        """Leave an existing lobby"""
        lobbyToken = self.active_connections[websocket]
        if lobbyToken:
            nickname = self.active_games[lobbyToken]["connected"][websocket]
            del self.active_games[lobbyToken]["connected"][websocket]
            print(f"{websocket.client} was in room {lobbyToken} - removing from room")
            if len(self.active_games[lobbyToken]["connected"]) == 0:
                del self.active_games[lobbyToken]
                print("Room is empty - closing")
            else:
                event = {"type": "leave_lobby", "data": {nickname: "left"}}
                await self.send(self.active_games[lobbyToken]["connected"].keys(), event)

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
                        if self.active_games[game]["lobby_name"] == data["data"]["lobby_name"]:
                            if len(self.active_games[game]["connected"]) > 3:
                                raise LobbyException(action="join_lobby", field="lobby_name", message="room is full")
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
                                    "data": {
                                        "lobby_token": game,
                                        "connected": list(self.active_games[game]["connected"].values()),
                                    },
                                },
                            )
                            return
                    raise LobbyException(action="join_lobby", field="lobby_name", message="not found")
                case "ready_up":
                    if data["data"].get("status", None) not in ["ready", "not ready"]:
                        raise LobbyException(action="ready_up", field="status", message="invalid status")
                    lobbyToken = self.active_connections[websocket]
                    nickname = self.active_games[lobbyToken]["connected"][websocket]
                    self.active_games[lobbyToken]["status"][nickname] = data["data"]["status"]
                    await self.send(
                        websockets=self.active_games[lobbyToken]["connected"],
                        data={"type": "ready_up", "data": {"ready": self.active_games[lobbyToken]["status"]}},
                    )

                    ready = 0
                    for user in self.active_games[lobbyToken]["status"].values():
                        if user == "ready":
                            ready += 1
                    if ready == 4:
                        self.active_games[lobbyToken]["game"] = Game(self.active_games[lobbyToken]["connected"], self)
                        await self.send(self.active_games[lobbyToken]["connected"], {"type": "start"})
                        data = self.active_games[lobbyToken]["game"].game_start()
                        for event in data:
                            user = event.pop("user")
                            await self.send(websockets=[user], data=event)
                case "leave_lobby":
                    await self.leave_lobby(websocket)
                    return
                case "phase_1" | "phase_2":
                    self.active_games[self.active_connections[websocket]]["game"].receive(data)
                case _:
                    raise LobbyException(
                        action=data["type"],
                        field="type",
                        message="unimplemented/bad request",
                    )

        except KeyError as e:
            action = data.get("type", None)
            await self.send(
                websockets=[websocket],
                data={"type": action, "error": {"Missing key": e.args[0]}},
            )

        except LobbyException as e:
            await self.send(websockets=[websocket], data=e.as_json())

    async def send(self, websockets: List[WebSocket], data: Any):
        """Send data to one or more clients"""
        if type(data) is dict:
            for websocket in websockets:
                await websocket.send_json(data)
        else:  # Should never happen!
            for websocket in websockets:
                await websocket.send_json({"message": data})

    async def disconnect(self, websocket: WebSocket) -> None:
        """Handle disconnection of a websocket."""
        print(f"{websocket.client} has disconnected - removing.")
        await self.leave_lobby(websocket)
        del self.active_connections[websocket]
