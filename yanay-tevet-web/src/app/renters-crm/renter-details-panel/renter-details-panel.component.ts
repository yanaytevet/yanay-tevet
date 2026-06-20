import {Component, input} from '@angular/core';
import {DatePipe} from '@angular/common';
import {RenterProspectSchema} from '../../../generated-files/api/renters-crm';
import {FAMILY_STATUS_LABELS} from '../renters-crm.constants';

@Component({
  selector: 'app-renter-details-panel',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './renter-details-panel.component.html',
})
export class RenterDetailsPanelComponent {
  readonly renter = input.required<RenterProspectSchema>();
  readonly currencySymbol = input.required<string>();

  readonly familyStatusLabels = FAMILY_STATUS_LABELS;
}
