import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { passwordMatchValidator } from '../../validators/password-match.validator';
import { BehaviorSubject } from 'rxjs';
import { MatRadioModule } from '@angular/material/radio';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { CommunicationService } from '../../services/communication.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-authorization',
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
    MatRadioModule,
    MatSlideToggleModule,
    HttpClientModule,
  ],
  templateUrl: './authorization.component.html',
  styleUrl: './authorization.component.scss'
})
export class AuthorizationComponent implements OnInit{
  isSignUp: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false)

  fb = inject(FormBuilder)
  communicationService = inject(CommunicationService)


  form = this.fb.group({
    username: new FormControl(null, [Validators.required]),
    password: new FormControl(null, [Validators.required, Validators.minLength(8)]),
  })

  ngOnInit(): void {
    (this.form as any).setControl(
      'confirmPassword',
      new FormControl(null, [Validators.required, Validators.minLength(8)])
    );
    this.form.addValidators(passwordMatchValidator('password', 'confirmPassword'))
    this.form.valueChanges.subscribe(data => {
      console.log(data);
      
    })
    this.isSignUp.subscribe(value => {
      if (value) {
        (this.form as any).setControl(
          'confirmPassword',
          new FormControl(null, [Validators.required, Validators.minLength(8)])
        );
        this.form.addValidators(passwordMatchValidator('password', 'confirmPassword'));
      } else {
        this.form.removeValidators(passwordMatchValidator('password', 'confirmPassword'));
        (this.form as any).removeControl('confirmPassword');
      }
    })
  }

  login(username: string, password: string) {
    this.communicationService.login(username, password);
  }

  register(username: string, password: string) {
    this.communicationService.register(username, password);
  }

  submitButton() {
    if (this.form.valid) {
      this.isSignUp.value 
      ? this.register(this.form.controls.username.value!, this.form.controls.password.value!)
      : this.login(this.form.controls.username.value!, this.form.controls.password.value!)
    }
  }

}
