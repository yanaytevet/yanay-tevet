import {Component, inject, OnInit} from '@angular/core';

import {postSampleWebsocketView} from '../../../generated-files/api/blocks';
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
    isActive = false;

    constructor() {
        super();
    }

    ngOnInit(): void {
        this.addWsSubscriptions();
    }

    async addWsSubscriptions() {
        await this.userWebsocketsService.finishedConnecting();
        this.subscriptions.push(await this.userWebsocketsService.websocketGroupSubscribe('room', {'room_id': 1},
            (data: WebsocketEvent) => {
                this.events.push(`Room 1: ${data.payload['message']}`);
            }));
        this.subscriptions.push(await this.userWebsocketsService.websocketGroupSubscribe('room', {'room_id': 2},
            (data: WebsocketEvent) => {
                this.events.push(`Room 2: ${data.payload['message']}`);
            }));
        this.isActive = true;
    }

    async triggerEventA() {
        await postSampleWebsocketView({body: {room_id: 1}});
    }

    async triggerEventB() {
        await postSampleWebsocketView({body: {room_id: 2}});
    }
}
