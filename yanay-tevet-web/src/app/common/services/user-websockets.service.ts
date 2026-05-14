import {inject, Injectable} from '@angular/core';
import {BehaviorSubject, Subject, Subscription} from "rxjs";
import {StringUtilsService} from './string-utils.service';
import {AuthenticationService} from '../authentication/authentication.service';
import {WebsocketEvent} from '../interfaces/websockets/websocket-event';
import {environment} from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})

export class UserWebsocketsService {
  TIMEOUT_MS = 30000;
  stringUtils = inject(StringUtilsService);
  authService = inject(AuthenticationService);

  private ws: WebSocket = null;
  private readonly _websocketIsReady = new BehaviorSubject<boolean>(false);
  readonly websocketIsReady$ = this._websocketIsReady.asObservable();

  private readonly _websocketListener = new Subject<WebsocketEvent>();
  readonly websocketListener$ = this._websocketListener.asObservable();

  private readonly _websocketConnectedToGroupListener = new Subject<WebsocketEvent>();
  readonly websocketConnectedToGroupListener$ = this._websocketConnectedToGroupListener.asObservable();

  constructor() {
    this.authService.auth$.subscribe(async (authUser) => {
      if (authUser && !this._websocketIsReady.getValue()) {
        await this.disconnect();
        await this.connect();
      }
    });
  }

  private getApiUrl(): string {
    return environment.apiUrl.split('//')[1];
  }

  public async connect() {
    // sleep for 1 second to allow the server to start
    await new Promise(resolve => setTimeout(resolve, 1000));
    const usesSsl = location.protocol === "https:";
    const protocol = usesSsl ? 'wss' : 'ws';
    const url = `${protocol}://${this.getApiUrl()}/ws/socket/`;
    this.ws = new WebSocket(url);
    this.ws.onmessage = (event) => {
      const eventJsonData: WebsocketEvent = JSON.parse(event.data);
      if (eventJsonData.is_connection_event) {
        this._websocketConnectedToGroupListener.next(eventJsonData);
      } else {
        this._websocketListener.next(eventJsonData);
      }
    }
    this.ws.onopen = () => {
      this._websocketIsReady.next(true);
    };
  }

  public async disconnect() {
    if (!this.ws) {
      return;
    }
    this._websocketIsReady.next(false);
    this.ws.close();
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
      this.ws.send(JSON.stringify({
        'action': 'subscribe',
        'action_hash': actionHash,
        'event_type': eventType,
        'additional_info': additionalInfo,
        'access_token': this.authService.accessToken(),
      }));
    });
    return this.websocketListener$.subscribe((data: WebsocketEvent) => {
      if (data && data.group_name === groupInfo.group_name) {
        callback(data);
      }
    });
  }

}
