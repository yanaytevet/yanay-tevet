import {Component} from '@angular/core';
import {RouterOutlet} from '@angular/router';
import {CelebrationOverlayComponent} from './common/components/celebration/celebration-overlay.component';
import {VersionUpdateBannerComponent} from './common/components/version-update-banner/version-update-banner.component';

@Component({
    selector: 'app-root',
    imports: [RouterOutlet, CelebrationOverlayComponent, VersionUpdateBannerComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})
export class AppComponent {
}
