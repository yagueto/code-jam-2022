from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from utils.ConnectionManager import WebsocketManager

app = FastAPI()
connection_manager: WebsocketManager = WebsocketManager()


@app.exception_handler(404)
async def custom_404_handler(_, __):
    """Handler for any 404 errors."""
    return RedirectResponse(url="/index.html", status_code=301)


@app.get("/")
def redirect_to_main():
    """Test endpoint. Will return the main page."""
    return RedirectResponse(url="/index.html", status_code=301)


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
    await connection_manager.connect(websocket=websocket)
    try:
        while True:
            await connection_manager.receive(websocket=websocket)
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket=websocket)


app.mount(
    "/",
    StaticFiles(directory="./static", html=False),
    name="static",
)
