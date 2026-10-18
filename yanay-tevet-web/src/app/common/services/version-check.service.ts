import {DestroyRef, inject, Injectable, signal} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {NavigationEnd, Router} from '@angular/router';
import {filter} from 'rxjs';

// The production build names its entry bundles by content hash, so the pair of names in index.html
// changes exactly when the deployed code does. `ng serve` emits unhashed names, which disables the check.
const HASHED_ENTRY_ASSET_PATTERN = /\b(?:main|styles)-[A-Z0-9]+\.(?:js|css)\b/g;

/**
 * Notices that a newer deployment is live under an already-open tab, by comparing the hashed entry
 * bundles this tab booted from against the ones a freshly fetched index.html points to.
 *
 * Deliberately not a service worker: `SwUpdate` answers the same question, but a registered worker
 * takes over caching for the whole origin and needs a planned unregister path to back out.
 */
@Injectable({
    providedIn: 'root'
})
export class VersionCheckService {
    private readonly POLL_MS = 5 * 60 * 1000;
    private readonly MIN_GAP_BETWEEN_CHECKS_MS = 30 * 1000;

    private readonly document = inject(DOCUMENT);
    private readonly destroyRef = inject(DestroyRef);
    private readonly router = inject(Router);

    private readonly runningFingerprint = this.readRunningFingerprint();

    private readonly _latestFingerprint = signal<string | null>(null);
    /** The deployed build's fingerprint, set only once it is known to differ from the running one. */
    readonly latestFingerprint = this._latestFingerprint.asReadonly();

    private lastCheckedAtMs = 0;
    private pollTimer: ReturnType<typeof setInterval> | null = null;

    constructor() {
        if (!this.runningFingerprint) {
            return;
        }
        this.document.addEventListener('visibilitychange', this.onVisibilityChange);
        window.addEventListener('pageshow', this.onPageShow);
        window.addEventListener('online', this.onOnline);
        this.router.events
            .pipe(filter(event => event instanceof NavigationEnd))
            .subscribe(() => this.checkNow());
        this.destroyRef.onDestroy(() => this.stop());
        if (this.document.visibilityState === 'visible') {
            this.startPolling();
        }
    }

    reloadToLatest(): void {
        window.location.reload();
    }

    private readonly onVisibilityChange = (): void => {
        if (this.document.visibilityState === 'visible') {
            this.checkNow();
            this.startPolling();
        } else {
            // Phones keep tabs open for days; a hidden one doesn't poll, and showing it checks at once.
            this.stopPolling();
        }
    };

    // iPhone Safari restores a page from its back-forward cache without always firing visibilitychange.
    private readonly onPageShow = (event: PageTransitionEvent): void => {
        if (event.persisted) {
            this.checkNow();
            this.startPolling();
        }
    };

    // A phone back from no signal checks at once rather than at the next poll.
    private readonly onOnline = (): void => {
        this.checkNow();
    };

    private startPolling(): void {
        if (this.pollTimer === null) {
            this.pollTimer = setInterval(() => this.checkNow(), this.POLL_MS);
        }
    }

    private stopPolling(): void {
        if (this.pollTimer !== null) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    private stop(): void {
        this.stopPolling();
        this.document.removeEventListener('visibilitychange', this.onVisibilityChange);
        window.removeEventListener('pageshow', this.onPageShow);
        window.removeEventListener('online', this.onOnline);
    }

    private async checkNow(): Promise<void> {
        if (this._latestFingerprint() !== null) {
            return;
        }
        const nowMs = Date.now();
        if (nowMs - this.lastCheckedAtMs < this.MIN_GAP_BETWEEN_CHECKS_MS) {
            return;
        }
        this.lastCheckedAtMs = nowMs;
        const deployedFingerprint = await this.fetchDeployedFingerprint();
        if (deployedFingerprint && deployedFingerprint !== this.runningFingerprint) {
            this._latestFingerprint.set(deployedFingerprint);
            this.stop();
        }
    }

    private readRunningFingerprint(): string {
        const urls = Array.from(this.document.querySelectorAll<HTMLScriptElement | HTMLLinkElement>('script[src], link[rel="stylesheet"][href]'))
            .map(element => element.getAttribute('src') ?? element.getAttribute('href') ?? '');
        return this.fingerprintOf(urls.join(' '));
    }

    private async fetchDeployedFingerprint(): Promise<string | null> {
        try {
            // The query param defeats intermediary caches; `no-store` only binds the browser's own. `/` rather
            // than `/index.html`, which Cloudflare answers with a redirect to `/`.
            const response = await fetch(`/?t=${Date.now()}`, {cache: 'no-store'});
            if (!response.ok) {
                return null;
            }
            // Mid-deploy the page can briefly come back without the bundles; that is not a new version.
            return this.fingerprintOf(await response.text()) || null;
        } catch {
            return null;
        }
    }

    private fingerprintOf(html: string): string {
        return Array.from(new Set(html.match(HASHED_ENTRY_ASSET_PATTERN) ?? [])).sort().join(',');
    }
}
