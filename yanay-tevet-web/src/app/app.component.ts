import {Component, inject} from '@angular/core';
import {RouterOutlet} from '@angular/router';
import {CelebrationOverlayComponent} from './common/components/celebration/celebration-overlay.component';
import {VersionUpdateBannerComponent} from './common/components/version-update-banner/version-update-banner.component';
import {AppAccentService} from './shared/apps/app-accent.service';

@Component({
    selector: 'app-root',
    imports: [RouterOutlet, CelebrationOverlayComponent, VersionUpdateBannerComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})
export class AppComponent {
    // Created here so the accent follows navigation from the first page on.
    private readonly appAccentService = inject(AppAccentService);
}
