import { Component, inject, OnInit } from '@angular/core';
import { CommunicationService } from '../../services/communication.service';
import { ResultItemComponent } from '../../components/result-item/result-item.component';
import { Result } from '../../interfaces/interfaces';
import { MatExpansionModule } from '@angular/material/expansion';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [ResultItemComponent, MatExpansionModule],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss'
})
export class HistoryComponent implements OnInit {
  results: Result[] = [];
  data: { result: Result, username: string, timestamp: string }[] = []
  communicationService = inject(CommunicationService)

  ngOnInit(): void {
    this.communicationService.getSavedResults().subscribe((results) => {
      console.log(results);
      this.data = results.data;
      this.results = results.data.map(res => res.result).flat();
    })
  }
}
