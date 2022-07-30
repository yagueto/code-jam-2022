import { Component } from '@angular/core';
import { LoadingService } from './loading.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  loading: boolean = false;

  constructor (private loadingManager: LoadingService) {
    this.loadingManager.onLoadingChange.subscribe((val) => this.loading = val);
  }
}
