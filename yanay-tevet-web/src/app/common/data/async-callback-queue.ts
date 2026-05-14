export type AsyncCallback<T> = () => Promise<T>;

/**
 * Runs async callbacks strictly one-at-a-time, in the order they were enqueued.
 * - FIFO
 * - Does not stop on errors (a failed task doesn't block later tasks)
 * - Optional: clear pending tasks
 */
export class AsyncCallbackQueue {
  private tail: Promise<void> = Promise.resolve();
  private pendingCount = 0;
  private clearToken = 0; // used to invalidate queued-but-not-started tasks

  /**
   * Enqueue an async callback. Returns a promise for that callback's result.
   */
  enqueue<T>(cb: AsyncCallback<T>): Promise<T> {
    const tokenAtEnqueue = this.clearToken;
    this.pendingCount++;

    const run = async (): Promise<T> => {
      // If queue was cleared after this was enqueued but before it started, cancel it.
      if (tokenAtEnqueue !== this.clearToken) {
        throw new Error("AsyncCallbackQueue: task cancelled (queue cleared).");
      }
      return cb();
    };

    const resultPromise = this.tail.then(run);

    // Advance the tail regardless of success/failure so the queue keeps flowing.
    this.tail = resultPromise
      .then(
        () => undefined,
        () => undefined,
      )
      .finally(() => {
        this.pendingCount--;
      });

    return resultPromise;
  }

  /**
   * Clears tasks that haven't started yet.
   * In-flight task continues (can't be safely aborted without AbortSignal support).
   */
  clear(): void {
    this.clearToken++;
  }

  /**
   * Returns how many tasks are waiting/running.
   * (Includes the in-flight one, if any.)
   */
  size(): number {
    return this.pendingCount;
  }

  /**
   * Resolves when all tasks currently queued (and any in-flight) have finished.
   */
  async onIdle(): Promise<void> {
    await this.tail;
  }
}
