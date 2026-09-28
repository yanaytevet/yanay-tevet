import {ErrorHandler, Injectable} from '@angular/core';
import {NavigationError} from '@angular/router';

/**
 * Recovers a tab whose lazy chunks no longer exist on the server.
 *
 * After a deploy, a tab opened before it asks for hashed chunks that are now 404s, and the lazy
 * navigation dies silently. Reloading is the only cure, and it is safe because the page is already broken.
 */
const CHUNK_LOAD_FAILURE_PATTERNS = [
    /Failed to fetch dynamically imported module/i,
    /error loading dynamically imported module/i,
    /Importing a module script failed/i,
    /Loading chunk \S+ failed/i,
    /Loading CSS chunk \S+ failed/i,
];

// A chunk can 404 for reasons a reload won't fix (a broken deploy, a blocking extension);
// this keeps the recovery from turning into a reload loop.
const RELOAD_MARKER_KEY = 'yanay-tevet-chunk-reload-at';
const MIN_GAP_BETWEEN_RELOADS_MS = 60 * 1000;

export function isChunkLoadError(error: unknown): boolean {
    if (!error) {
        return false;
    }
    if (error instanceof Error && error.name === 'ChunkLoadError') {
        return true;
    }
    const message = error instanceof Error ? error.message : String(error);
    return CHUNK_LOAD_FAILURE_PATTERNS.some(pattern => pattern.test(message));
}

export function reloadAfterChunkLoadError(): void {
    const nowMs = Date.now();
    let lastReloadAtMs = 0;
    try {
        lastReloadAtMs = Number(sessionStorage.getItem(RELOAD_MARKER_KEY) ?? 0);
    } catch {
        // Private-mode storage can throw; treating it as never-reloaded costs at most one extra reload.
    }
    if (nowMs - lastReloadAtMs < MIN_GAP_BETWEEN_RELOADS_MS) {
        console.error('A lazy chunk failed to load again right after reloading; not reloading a second time.');
        return;
    }
    try {
        sessionStorage.setItem(RELOAD_MARKER_KEY, String(nowMs));
    } catch {
        // A reload we cannot record is still better than a dead page.
    }
    window.location.reload();
}

@Injectable()
export class ChunkLoadErrorHandler implements ErrorHandler {
    handleError(error: unknown): void {
        if (isChunkLoadError(error)) {
            reloadAfterChunkLoadError();
            return;
        }
        console.error(error);
    }
}

export function handleChunkLoadNavigationError(navigationError: NavigationError): void {
    if (isChunkLoadError(navigationError.error)) {
        reloadAfterChunkLoadError();
    }
}
