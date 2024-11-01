import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-result-item',
  standalone: true,
  imports: [MatCardModule],
  templateUrl: './result-item.component.html',
  styleUrl: './result-item.component.scss'
})
export class ResultItemComponent {
  path = 'assets/images/'

  @Input() pictureName!: string;
}
