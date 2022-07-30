import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AboutComponent } from './_pages/about/about.component';
import { LobbyComponent } from './_pages/lobby/lobby.component';
import { PhaseOneComponent } from './_pages/phase-one/phase-one.component';

const routes: Routes = [
  { path: "lobby", component: LobbyComponent},
  { path: "phase-one", component: PhaseOneComponent},
  { path: "", component: AboutComponent},
  { path: '**', redirectTo: '/' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
