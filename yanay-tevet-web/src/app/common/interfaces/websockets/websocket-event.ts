export interface WebsocketEvent {
  is_connection_event: boolean;
  action_hash: string;
  group_name: string;
  event_type: string;
  payload: Record<string, any>;
}
