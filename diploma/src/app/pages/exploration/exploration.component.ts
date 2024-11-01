import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { combineLatestWith, Subscription } from 'rxjs';
import { CommunicationService } from '../../services/communication.service';
import { HttpClientModule } from '@angular/common/http';
import { ResultItemComponent } from "../../components/result-item/result-item.component";

interface SelectOptions {
  value: number,
  displayValue: string
}

@Component({
  selector: 'app-exploration',
  standalone: true,
  imports: [
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatListModule,
    HttpClientModule,
    ResultItemComponent
],
  templateUrl: './exploration.component.html',
  styleUrl: './exploration.component.scss',
  providers: [CommunicationService]
})
export class ExplorationComponent implements OnInit, OnDestroy {

  public startButtonDisabled: boolean = true;
  public resultImages: string[] = [];

  data!: any;

  fb = inject(FormBuilder)
  communicationService = inject(CommunicationService)

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
    dencity: new FormControl(null, [Validators.required]),
    time: new FormControl(null, [Validators.required, Validators.min(0)])
  })

  private subscription = new Subscription()

  ngOnInit(): void {
    this.subscription.add(this.formSubscription());
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  getForm() {
    console.log(this.form.getRawValue());
    this.communicationService.startSimulation()
      .pipe(combineLatestWith(this.communicationService.getPictures()))
      .subscribe(([results, pictures]) => {
        this.data = results;
        this.resultImages = pictures;
        console.log('completed');
      })
  }

  getResults () {
    this.communicationService.getPictures().subscribe(data => {
      console.log(data);
      this.resultImages = data
    })
  }

  resetTime () {
    this.form.controls.time.setValue(null);
  }

  formSubscription() {
    return this.form.statusChanges.subscribe((status) => {
      this.startButtonDisabled = !(status === 'VALID');
    })
  }

}
