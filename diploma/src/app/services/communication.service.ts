import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CommunicationService {

  private apiUrl = 'http://localhost:5000';

  hc = inject(HttpClient)

  constructor() { }

  getPictures () {
    return this.hc.get(this.apiUrl + '/get_images') as Observable<string[]>
  }

  startSimulation() {
    return this.hc.post(this.apiUrl + '/start_mapping', { dencity: 3, time: 30 })
  }

}
