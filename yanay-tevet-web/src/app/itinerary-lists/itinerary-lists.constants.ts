import {ItemStatus, ListStatus} from '../../generated-files/api/itinerary-lists';

export const ITEM_STATUS_LABELS: Record<ItemStatus, string> = {
  need_to_buy: 'Need to buy',
  in_the_house: 'In the house',
  ready: 'Ready',
  in_the_car: 'In the car',
};

export const ITEM_STATUS_ORDER: ItemStatus[] = ['need_to_buy', 'in_the_house', 'ready', 'in_the_car'];

// Tap-to-cycle advances forward through this progression and stops at the terminal status.
export const ITEM_STATUS_NEXT: Record<ItemStatus, ItemStatus> = {
  need_to_buy: 'in_the_house',
  in_the_house: 'ready',
  ready: 'in_the_car',
  in_the_car: 'in_the_car',
};

export const ITEM_STATUS_CHIP_CLASS: Record<ItemStatus, string> = {
  need_to_buy: 'status-need-buy',
  in_the_house: 'status-in-house',
  ready: 'status-ready',
  in_the_car: 'status-in-car',
};

export const LIST_STATUS_LABELS: Record<ListStatus, string> = {
  standby: 'Standby',
  active: 'Active',
};
