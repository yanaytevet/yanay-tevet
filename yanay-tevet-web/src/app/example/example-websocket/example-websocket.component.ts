import {Component, inject, OnInit} from '@angular/core';

import {postSampleWebsocketView} from '../../../generated-files/api/blocks';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {BasePageComponent} from '../../common/components/base-page-component';
import {UserWebsocketsService} from '../../common/services/user-websockets.service';
import {WebsocketEvent} from '../../common/interfaces/websockets/websocket-event';

@Component({
    selector: 'app-example-websocket',
    imports: [],
    templateUrl: './example-websocket.component.html',
    styleUrl: './example-websocket.component.css'
})
export class ExampleWebsocketComponent extends BasePageComponent implements OnInit {
    events: string[] = [];
    userWebsocketsService = inject(UserWebsocketsService);
    private readonly authService = inject(AuthenticationService);
    isActive = false;

    constructor() {
        super();
    }

    ngOnInit(): void {
        this.addWsSubscriptions();
    }

    // The backend refuses a notifications group named after anybody else's id, so the signed-in
    // user's own is the only one worth asking for.
    async addWsSubscriptions() {
        await this.userWebsocketsService.finishedConnecting();
        const userId = this.authService.user()?.id;
        if (!userId) {
            return;
        }
        this.subscriptions.push(await this.userWebsocketsService.websocketGroupSubscribe('user_notifications', {'user_id': userId},
            (data: WebsocketEvent) => {
                this.events.push(`${data.payload['message']}`);
            }));
        this.isActive = true;
    }

    async triggerEventA() {
        await postSampleWebsocketView({body: {message: 'Hello from websocket! (A)'}});
    }

    async triggerEventB() {
        await postSampleWebsocketView({body: {message: 'Hello from websocket! (B)'}});
    }
}
