import {inject, Injectable} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {BehaviorSubject, Subject, Subscription} from "rxjs";
import {StringUtilsService} from './string-utils.service';
import {AuthenticationService} from '../authentication/authentication.service';
import {WebsocketEvent} from '../interfaces/websockets/websocket-event';
import {environment} from '../../../environments/environment';

interface ActiveSubscription {
  eventType: string;
  additionalInfo: object;
}

@Injectable({
  providedIn: 'root'
})

export class UserWebsocketsService {
  TIMEOUT_MS = 30000;
  // A light app-level ping keeps idle proxies from dropping the socket; the consumer ignores anything
  // that isn't a subscribe.
  HEARTBEAT_MS = 30000;
  RECONNECT_BASE_MS = 1000;
  RECONNECT_MAX_MS = 30000;

  stringUtils = inject(StringUtilsService);
  authService = inject(AuthenticationService);
  private readonly document = inject(DOCUMENT);

  private ws: WebSocket = null;
  // Whether we want a live connection. Set false only on an intentional disconnect, so a normal drop
  // (a deploy, a network change on a phone) reconnects but an explicit disconnect stays down.
  private shouldReconnect = false;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> = null;
  private heartbeatTimer: ReturnType<typeof setInterval> = null;
  // Active group subscriptions, keyed by action hash, replayed after every reconnect so live updates
  // resume without the pages having to subscribe again.
  private readonly activeSubscriptions = new Map<string, ActiveSubscription>();

  private readonly _websocketIsReady = new BehaviorSubject<boolean>(false);
  readonly websocketIsReady$ = this._websocketIsReady.asObservable();

  private readonly _websocketListener = new Subject<WebsocketEvent>();
  readonly websocketListener$ = this._websocketListener.asObservable();

  private readonly _websocketConnectedToGroupListener = new Subject<WebsocketEvent>();
  readonly websocketConnectedToGroupListener$ = this._websocketConnectedToGroupListener.asObservable();

  constructor() {
    this.authService.auth$.subscribe(async (authUser) => {
      if (authUser && !this._websocketIsReady.getValue()) {
        await this.connect();
      }
    });
    // A phone back from no signal, or a tab brought back to the front, reconnects at once rather than
    // waiting out the backoff.
    window.addEventListener('online', this.reconnectNow);
    this.document.addEventListener('visibilitychange', () => {
      if (this.document.visibilityState === 'visible') {
        this.reconnectNow();
      }
    });
  }

  private getApiUrl(): string {
    return environment.apiUrl.split('//')[1];
  }

  public async connect() {
    this.shouldReconnect = true;
    this.openSocket();
  }

  private readonly reconnectNow = (): void => {
    if (!this.shouldReconnect || this.isOpenOrOpening()) {
      return;
    }
    this.reconnectAttempts = 0;
    this.openSocket();
  };

  private isOpenOrOpening(): boolean {
    return !!this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING);
  }

  private openSocket() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    // Never stack a second socket on top of a live or opening one.
    if (this.isOpenOrOpening()) {
      return;
    }
    const usesSsl = location.protocol === "https:";
    const protocol = usesSsl ? 'wss' : 'ws';
    const url = `${protocol}://${this.getApiUrl()}/ws/socket/`;
    const ws = new WebSocket(url);
    this.ws = ws;
    ws.onmessage = (event) => {
      const eventJsonData: WebsocketEvent = JSON.parse(event.data);
      if (eventJsonData.is_connection_event) {
        this._websocketConnectedToGroupListener.next(eventJsonData);
      } else {
        this._websocketListener.next(eventJsonData);
      }
    };
    ws.onopen = async () => {
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      await this.resubscribeAll();
      this._websocketIsReady.next(true);
    };
    ws.onclose = () => this.handleDrop(ws);
    ws.onerror = () => this.handleDrop(ws);
  }

  private handleDrop(ws: WebSocket) {
    // Ignore drops from a socket that has already been replaced or torn down.
    if (ws !== this.ws) {
      return;
    }
    this.teardownSocket();
    this._websocketIsReady.next(false);
    if (this.shouldReconnect) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) {
      return;
    }
    const delay = Math.min(this.RECONNECT_BASE_MS * (2 ** this.reconnectAttempts), this.RECONNECT_MAX_MS);
    this.reconnectAttempts += 1;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.openSocket();
    }, delay);
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({'action': 'ping'}));
      }
    }, this.HEARTBEAT_MS);
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private teardownSocket() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.close();
      this.ws = null;
    }
  }

  private async resubscribeAll() {
    if (this.activeSubscriptions.size === 0) {
      return;
    }
    const accessToken = await this.authService.freshAccessToken();
    for (const [actionHash, subscription] of this.activeSubscriptions) {
      this.sendSubscribe(actionHash, subscription.eventType, subscription.additionalInfo, accessToken);
    }
  }

  private sendSubscribe(actionHash: string, eventType: string, additionalInfo: object, accessToken: string): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return false;
    }
    this.ws.send(JSON.stringify({
      'action': 'subscribe',
      'action_hash': actionHash,
      'event_type': eventType,
      'additional_info': additionalInfo,
      'access_token': accessToken,
    }));
    return true;
  }

  public async disconnect() {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.teardownSocket();
    this._websocketIsReady.next(false);
  }

  public async finishedConnecting() {
    await this.authService.waitForAuth();
    await new Promise(resolve => {
      this.websocketIsReady$.subscribe((isReady: boolean) => {
        if (isReady) {
          resolve(null);
        }
      });
    });
  }


  public async websocketGroupSubscribe(eventType: string, additionalInfo: object, callback: (data: WebsocketEvent) => void): Promise<Subscription> {
    let groupInfo: WebsocketEvent = null;
    const actionHash = this.stringUtils.generateRandomString(32);
    // Remembered so the subscription is replayed after any reconnect.
    this.activeSubscriptions.set(actionHash, {eventType, additionalInfo});
    const accessToken = await this.authService.freshAccessToken();
    await new Promise(resolve => {
      setTimeout(() => {
        resolve(false);
      }, this.TIMEOUT_MS);
      this.websocketConnectedToGroupListener$.subscribe((data: WebsocketEvent) => {
        if (data && data.action_hash === actionHash) {
          groupInfo = data;
          resolve(true);
        }
      });
      this.sendSubscribe(actionHash, eventType, additionalInfo, accessToken);
    });
    const listenerSubscription = this.websocketListener$.subscribe((data: WebsocketEvent) => {
      // groupInfo stays null when the server refused the subscription and never answered it.
      if (data && groupInfo && data.group_name === groupInfo.group_name) {
        callback(data);
      }
    });
    // Stop replaying this subscription once the caller tears it down.
    return new Subscription(() => {
      this.activeSubscriptions.delete(actionHash);
      listenerSubscription.unsubscribe();
    });
  }

}
