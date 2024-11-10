import { Component, Input, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { Result } from '../../interfaces/interfaces';
import { MatListModule } from '@angular/material/list';
import { MatExpansionModule } from '@angular/material/expansion';

@Component({
  selector: 'app-result-item',
  standalone: true,
  imports: [MatCardModule, MatListModule, MatExpansionModule],
  templateUrl: './result-item.component.html',
  styleUrl: './result-item.component.scss'
})
export class ResultItemComponent implements OnInit {
  @Input() pictureName!: string;
  @Input() result!: Result;
  @Input() index!: number;
  @Input() isResult: boolean = true;

  globalX: number[] = [];
  globalY: number[] = [];
  sensorAngles = [-20, -10, 0, 10, 20]


  path = 'http://127.0.0.1:10000/devstoreaccount1/pictures/'

  ngOnInit(): void {
    console.log(this.index);
    if (this.isResult) {
      this.calculation()
    }
  }

  calculation() {
    console.log(this.result);
    
    this.result.positions[this.index].distances.forEach((distance, i) => {
      if (distance !== null && this.result.positions) {
        const globalAngle = this.result.positions[this.index].orientation[2] +  (this.sensorAngles[i] * Math.PI / 180)
        

        const localX = distance * Math.cos(globalAngle);
        const localY = distance * Math.sin(globalAngle);

        this.globalX[i] = this.result.positions[this.index].position[0] + localX;
        this.globalY[i] = this.result.positions[this.index].position[1] + localY;

        // console.log(globalX);
        // console.log(globalY);
        
        
      } else {
        this.globalX[i] = 0;
        this.globalY[i] = 0;
      }
    })
  }

}
