import {Component} from '@angular/core';
import {RouterOutlet} from '@angular/router';
import {CelebrationOverlayComponent} from './common/components/celebration/celebration-overlay.component';

@Component({
    selector: 'app-root',
    imports: [RouterOutlet, CelebrationOverlayComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})
export class AppComponent {
}
