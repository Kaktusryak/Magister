import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterModule, MatButtonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'diploma';
}
