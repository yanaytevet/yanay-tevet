import {Component, input} from '@angular/core';
import {DatePipe} from '@angular/common';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapStar, bootstrapStarFill} from '@ng-icons/bootstrap-icons';
import {ApartmentProspectSchema} from '../../../generated-files/api/apartment-hunt';
import {CONTACT_METHOD_LABELS, LIKED_LEVELS} from '../apartment-hunt.constants';

@Component({
  selector: 'app-prospect-details-panel',
  standalone: true,
  imports: [NgIcon, DatePipe],
  providers: [provideIcons({bootstrapStar, bootstrapStarFill})],
  templateUrl: './prospect-details-panel.component.html',
})
export class ProspectDetailsPanelComponent {
  readonly prospect = input.required<ApartmentProspectSchema>();
  readonly currencySymbol = input.required<string>();

  readonly contactMethodLabels = CONTACT_METHOD_LABELS;
  readonly starLevels = LIKED_LEVELS;

  protected readonly bootstrapStar = bootstrapStar;
  protected readonly bootstrapStarFill = bootstrapStarFill;
}
