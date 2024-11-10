import { Component, inject } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { CommunicationService } from './services/communication.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterModule, MatButtonModule, HttpClientModule,],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  providers: [CommunicationService]
})
export class AppComponent {
  title = 'diploma';

  communicationService = inject(CommunicationService)

  unlog() {
    this.communicationService.unlog()
  }
}
