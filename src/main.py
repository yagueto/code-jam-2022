from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from utils.ConnectionManager import WebsocketManager

app = FastAPI()

connection_manager: WebsocketManager = WebsocketManager()


@app.get("/")
def hello():
    """Test endpoint. Will return the main page."""
    return {"hello": "world"}


@app.websocket("/ws")
async def websocket_test(websocket: WebSocket):
    """Test websocket."""
    # BasicReturnObject
    # {"type": functionName, "status": boolean, "data": any, "error": any}
    # type: which function was the data sent from # noqa: F723
    # status: was there an error or not?
    # data: if the status is true, the data from the function
    # error: if the status is true, what was the error
    #   -> if the error has a simple structure it can be just a: {"message": "Error message"}
    #   -> else the error should use an own dict structure with a self explanatory key
    #           for example: {"FormErrors": {"Username": {"MaxLenght": 12}, "LobbyName": {"MinLenght": 1}}}
    await websocket.accept()
    try:
        d = await websocket.receive_json()
        if d["type"] == "create_lobby":
            lobbyToken = await connection_manager.create_lobby(
                websocket, d["data"]["nickname"], d["data"]["lobbyName"]
            )
            await websocket.send_json(
                {
                    "type": "create_lobby",
                    "status": True,
                    "data": {"lobbyToken": lobbyToken},
                }
            )

    except WebSocketDisconnect:
        # TODO: Handle disconnections
        # connection_manager.disconnect(websocket)
        pass
    except NameError as e:
        await connection_manager.send(websocket, e)
