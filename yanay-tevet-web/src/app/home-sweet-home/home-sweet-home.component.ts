import {Component} from '@angular/core';
import {RouterOutlet} from '@angular/router';
import {HomeSweetHomeNavComponent} from './home-sweet-home-nav/home-sweet-home-nav.component';

@Component({
  selector: 'app-home-sweet-home',
  standalone: true,
  imports: [RouterOutlet, HomeSweetHomeNavComponent],
  templateUrl: './home-sweet-home.component.html',
})
export class HomeSweetHomeComponent {}
