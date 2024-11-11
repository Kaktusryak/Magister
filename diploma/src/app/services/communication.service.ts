import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Result } from '../interfaces/interfaces';
import { Router } from '@angular/router';
import { ProtectedResponse } from '../interfaces/interfaces'

@Injectable({
  providedIn: 'root'
})
export class CommunicationService {
  isLogged: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  username: BehaviorSubject<string | null> = new BehaviorSubject<string | null>(null);

  headers = new HttpHeaders().set('Authorization', `${this.getToken()}`);

  private apiUrl = 'http://localhost:5000';

  hc = inject(HttpClient)
  router = inject(Router)

  constructor() { }

  startSimulation(dencity: number | null, time: number | null) {
    return this.hc.post(this.apiUrl + '/start_mapping', { dencity: dencity || 3, time: time || 10 }) as Observable<Result>
  }

  login(username: string, password: string) {
    return this.hc.post(this.apiUrl + '/login', { username, password }).subscribe({
      next: (response: any) => {
        localStorage.setItem('token', response.token);
        this.isLogged.next(true);
        this.username.next(username)
        alert('Login successful');
        this.router.navigate(['/exploration']);
      },
      error: (error) => {
        alert('Login failed: ' + error.error.message);
      }
    })
  }

  register(username: string, password: string) {
    return this.hc.post(this.apiUrl + '/register', { username, password }).subscribe({
      next: () => {
        this.login(username, password);
      },
      error: (error) => {
        alert('Registration failed: ' + error.error.message);
      }
    })
  }

  restoreSession() {
    if (this.getToken()) {
      (this.hc.get(this.apiUrl + '/protected', { headers: this.headers }) as Observable<ProtectedResponse>).subscribe({
        next:(data: ProtectedResponse) => {
          console.log(data);
          this.isLogged.next(true);
          this.username.next(data.username)
          
        },
        error: (error) => {
          this.unlog()
        }
      })
    }

  }

  saveResults(username: string, result: Result) {
    return this.hc.post(this.apiUrl + '/save_result', { username, result }).subscribe(data => {
      console.log(data);
      
    })
  }

  getSavedResults() {
    return this.hc.get(this.apiUrl + '/results/' + this.username.value) as Observable<{ data: { result: Result, username: string, timestamp: string}[] , status: string }>
  }

  // Функція для отримання токена
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  // Функція для перевірки авторизації
  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  unlog() {
    localStorage.removeItem('token');
    this.username.next(null);
    this.isLogged.next(false)
  }

}
