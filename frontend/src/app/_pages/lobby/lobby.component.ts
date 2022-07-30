import { Component, OnDestroy, OnInit } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, Validators } from '@angular/forms';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';
import { SocketService } from 'src/app/socket.service';
import { player, wsResponse } from 'src/app/types';

@Component({
  selector: 'app-lobby',
  templateUrl: './lobby.component.html',
  styleUrls: ['./lobby.component.scss']
})
export class LobbyComponent implements OnInit, OnDestroy {
  fourCount = [0, 1, 2];

  currentState: "join" | "create" | "joined" = "create";
  loading: boolean = false;

  lobbyInfo: {token: string, name: string, me: {nickname: string, ready: boolean}, players: player[]} = {token: "", name: "", me: {nickname: "", ready: false}, players: []};
  wsFormError: {msg: string, type: "nickname" | "field"};

  mainForm: FormGroup;

  constructor(private router: Router, private socket: SocketService) {
    router.events.pipe(
      filter(event => event instanceof NavigationEnd)
      ).subscribe(() => {
        if (this.lobbyInfo.token) {
          this.socket.leave_lobby();
          this.lobbyInfo = {token: "", name: "", me: {nickname: "", ready: false}, players: []};
        }
        const nickname = (this.mainForm ? this.mainForm.get("nickname").value : null);
        this.checkUrlParams();
        this.mainForm = new FormGroup({
          "nickname": new FormControl(null, [Validators.required, Validators.maxLength(18)]),
          "field": new FormControl(null, [Validators.required, Validators.maxLength(16)])
        });
        if (nickname) {
          this.mainForm.reset({nickname: nickname});
        }
        this.wsFormError = null;
      });
    }

  ngOnDestroy(): void {
    if (this.lobbyInfo.token) {
      this.socket.leave_lobby();
    }
  }

  ngOnInit(): void {
    this.socket.init();
    this.socket.socketResponse.subscribe((val: wsResponse) => {
      this.loading = false;
      if (!val.status) {
        const key = "lobby_name" in val.error ? "lobby_name" : "nickname";
        this.wsFormError = {
          type: "lobby_name" in val.error ? "field" : "nickname",
          msg: val.error[key].charAt(0).toUpperCase() + val.error[key].slice(1) + "."
        }
        this.mainForm.reset(this.mainForm.value);
        return;
      }
      if (val.type === "create_lobby" || val.type === "join_lobby") {
        this.currentState = "joined";
        this.lobbyInfo.token = val.data["lobby_token"];
        window.history.replaceState("", "", window.location.origin + window.location.pathname);
      }
      if (val.type === "join_lobby") {
        if ("connected" in val.data) {
          const players: player[] = [];
          (val.data["connected"] as string[]).forEach((val) => {
            if (val !== this.lobbyInfo.me.nickname) {
              players.push({nickname: val, ready: false});
            }
          });
          this.lobbyInfo.players = [...players];
        } else {
          let name = Object.keys(val.data)[0];
          if (name === this.lobbyInfo.me.nickname) {return}
          this.lobbyInfo.players.push({
            nickname: name,
            ready: false
          });
        }
      } else if (val.type === "leave_lobby") {
        let index = this.getPlayerIndex(Object.keys(val.data)[0]);
        if (index === -1) {return}
        this.lobbyInfo.players.splice(index, 1);
      } else if (val.type === "ready_up") {
        for (const [k, v] of Object.entries(val.data["ready"] as object)) {
          if (k === this.lobbyInfo.me.nickname) {
            this.lobbyInfo.me.ready = v === "ready";
            continue;
          }
          let index = this.getPlayerIndex(k);
          if (index === -1) {continue;}
          let state = v === "ready";
          this.lobbyInfo.players[index].ready = state;
        }
      }
      console.log(val);
    });
  }

  getPlayerIndex(nickname: string) {
    for (let i = 0; i < this.lobbyInfo.players.length; i++) {
      if (nickname === this.lobbyInfo.players[i].nickname) {
        return i;
      }
    }
    return -1;
  }

  toggleReady() {
    this.socket.ready_up(!this.lobbyInfo.me.ready);
    this.lobbyInfo.me.ready = !this.lobbyInfo.me.ready;
  }

  checkUrlParams() {
    const hash = window.location.hash;
    const index = hash.indexOf("?");
    if (index === -1) {return;}
    const urlParams = new URLSearchParams(window.location.hash.slice(index));
    if (!(urlParams.has("action")) || (urlParams.get("action") != "join" && urlParams.get("action") != "create")) {return;}
    this.currentState = <"join" | "create">urlParams.get("action");
  }

  formSubmit() {
    const nickname = this.mainForm.get("nickname").value;
    const field = this.mainForm.get("field").value;
    if (this.currentState === "create") {
      this.socket.create_lobby(nickname, field);
    } else {
      this.socket.join_lobby(nickname, field);
    }
    this.lobbyInfo.name = field;
    this.lobbyInfo.me.nickname = nickname;
    this.lobbyInfo.me.ready = false;
    this.loading = true;
  }
}
