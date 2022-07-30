import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AboutComponent } from './_pages/about/about.component';
import { LobbyComponent } from './_pages/lobby/lobby.component';

const routes: Routes = [
  { path: "lobby", component: LobbyComponent},
  { path: "", component: AboutComponent},
  { path: '**', redirectTo: '/' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
