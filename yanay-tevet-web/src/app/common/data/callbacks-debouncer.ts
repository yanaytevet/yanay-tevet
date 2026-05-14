
/**
 * A utility class for debouncing callback functions.
 * This helps prevent excessive function calls, particularly useful for API requests
 * triggered by user interactions like typing, scrolling, or clicking.
 */
export class CallbacksDebouncer {
    private timeout: ReturnType<typeof setTimeout> = null;

    constructor(private timeoutMs = 200) {
    }

    public run(callback: () => void) {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
        this.timeout = setTimeout(callback, this.timeoutMs);
    }

    public clear() {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
    }
}
