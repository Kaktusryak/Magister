import { Component, inject } from '@angular/core';
import { FormBuilder, FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

interface SelectOptions {
  value: number,
  displayValue: string
}

@Component({
  selector: 'app-exploration',
  standalone: true,
  imports: [MatSelectModule, MatFormFieldModule, MatInputModule, FormsModule, ReactiveFormsModule, MatIconModule, MatButtonModule],
  templateUrl: './exploration.component.html',
  styleUrl: './exploration.component.scss'
})
export class ExplorationComponent {

  fb = inject(FormBuilder)

  public dencityOptions: SelectOptions[] = [
    {
      value: 1,
      displayValue: 'Small'
    },
    {
      value: 2,
      displayValue: 'Middle'
    },
    {
      value: 3,
      displayValue: 'High'
    }
  ]

  form = this.fb.group({
    dencity: new FormControl(this.dencityOptions[0]),
    time: new FormControl(null)
  })

  getForm() {
    console.log(this.form);
    
  }

}
