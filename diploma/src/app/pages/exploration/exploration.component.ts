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
import { Result, SelectOptions } from '../../interfaces/interfaces';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';


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
    ResultItemComponent,
    MatProgressSpinnerModule
],
  templateUrl: './exploration.component.html',
  styleUrl: './exploration.component.scss'
})
export class ExplorationComponent implements OnInit, OnDestroy {

  public startButtonDisabled: boolean = true;
  public isLoading: boolean = false;
  public resultImages: string[] = [];

  data!: Result;

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
    this.clearData();
    this.isLoading = true;
    this.startButtonDisabled = true;
    this.communicationService.startSimulation(this.form.controls.dencity.value, this.form.controls.time.value)
      .subscribe((results) => {
        this.data = results;
        console.log(results);
        this.getPictures()
        console.log('completed');
        this.startButtonDisabled = false;
        this.isLoading = false;
      })
  }

  getPictures () {
    this.resultImages = [];
    if (this.form.controls.time.value) {
      for (let i = 1; i <= this.form.controls.time.value; i++) {
        this.resultImages.push(`prediction_imageTest${i}.png`)
      }
    }
  }

  resetTime () {
    this.form.controls.time.setValue(null);
  }

  formSubscription() {
    return this.form.statusChanges.subscribe((status) => {
      this.startButtonDisabled = !(status === 'VALID');
    })
  }

  clearData() {
    this.data = {} as Result;
    this.resultImages = [];
  }

  saveResults() {
    if (this.communicationService.username.value && Object.keys(this.data).length) {
      console.log('save results');
      this.communicationService.saveResults(this.communicationService.username.value, this.data);
    }
  }

}
