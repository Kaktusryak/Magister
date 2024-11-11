import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { ExplorationComponent } from './pages/exploration/exploration.component';
import { AuthorizationComponent } from './pages/authorization/authorization.component';
import { HistoryComponent } from './pages/history/history.component';

export const routes: Routes = [
    { path: 'home', component: HomeComponent },
    { path: 'exploration', component: ExplorationComponent },
    { path: 'auth', component: AuthorizationComponent },
    { path: 'history', component: HistoryComponent },
    { path: '', component: HomeComponent },
    { path: '**', component: HomeComponent }
];
