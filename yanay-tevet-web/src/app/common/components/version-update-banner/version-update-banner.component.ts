import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapArrowClockwise} from '@ng-icons/bootstrap-icons';
import {featherX} from '@ng-icons/feather-icons';
import {VersionCheckService} from '../../services/version-check.service';

/**
 * Offers the reload rather than performing it, so half-filled forms aren't thrown away.
 * Tabs whose lazy chunks already 404'd are reloaded without asking by `ChunkLoadErrorHandler`.
 */
@Component({
    selector: 'app-version-update-banner',
    imports: [NgIcon],
    viewProviders: [provideIcons({bootstrapArrowClockwise, featherX})],
    templateUrl: './version-update-banner.component.html',
})
export class VersionUpdateBannerComponent {
    private readonly versionCheckService = inject(VersionCheckService);

    private readonly dismissedFingerprint = signal<string | null>(null);

    readonly showBanner = computed<boolean>(() => {
        const latestFingerprint = this.versionCheckService.latestFingerprint();
        return !!latestFingerprint && latestFingerprint !== this.dismissedFingerprint();
    });

    protected readonly bootstrapArrowClockwise = bootstrapArrowClockwise;
    protected readonly featherX = featherX;

    onReload(): void {
        this.versionCheckService.reloadToLatest();
    }

    onDismiss(): void {
        this.dismissedFingerprint.set(this.versionCheckService.latestFingerprint());
    }
}
