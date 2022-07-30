import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { environment } from "src/environments/environment";
import { wsResponse } from "./types";

@Injectable({providedIn: "root"})
export class SocketService {
    socket: WebSocket;
    socketResponse: Subject<{}> = new Subject<{}>();

    constructor () {}

    init() {
        this.socket = new WebSocket(environment.baseUrl);
        this.socket.onmessage = (data: MessageEvent) => {
            let json: wsResponse = JSON.parse(data.data);
            json.status = (json.error ? false : true);
            this.socketResponse.next(json);
        };
    }

    private send(data: object) {
        this.socket.send(JSON.stringify(data));
    }

    create_lobby(nickname: string, lobbyName: string) {
        this.send({type: "create_lobby", data: {nickname: nickname, lobby_name: lobbyName}});
    }

    join_lobby(nickname: string, lobbyName: string) {
        this.send({type: "join_lobby", data: {nickname: nickname, lobby_name: lobbyName}});
    }

    leave_lobby() {
        this.send({type: "leave_lobby"});
    }

    ready_up(state: boolean = true) {
        this.send({type: "ready_up", "data": {"status": (state ? "ready" : "not ready")}});
    }
}
