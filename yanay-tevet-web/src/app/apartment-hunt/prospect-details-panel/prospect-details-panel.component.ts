import {Component, computed, inject, input} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapStar, bootstrapStarFill} from '@ng-icons/bootstrap-icons';
import {ApartmentProspectSchema, Currency} from '../../../generated-files/api/apartment-hunt';
import {LIKED_LEVELS, moneyFormat, parseDate} from '../apartment-hunt.constants';
import {fill, injectStrings} from '../../shared/i18n/strings';
import {LanguageService} from '../../shared/i18n/language.service';
import {APARTMENT_HUNT_STRINGS} from '../i18n';

@Component({
  selector: 'app-prospect-details-panel',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({bootstrapStar, bootstrapStarFill})],
  templateUrl: './prospect-details-panel.component.html',
})
export class ProspectDetailsPanelComponent {
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(APARTMENT_HUNT_STRINGS);

  readonly prospect = input.required<ApartmentProspectSchema>();
  readonly currency = input.required<Currency>();

  readonly starLevels = LIKED_LEVELS;

  readonly roomsFloorSize = computed<string>(() => {
    const prospect = this.prospect();
    const number = (value: number | null) => (value === null ? '—' : value.toLocaleString(this.languageService.language()));
    return fill(this.t().panel.roomsFloorSizeValue, {
      rooms: number(prospect.rooms),
      floor: number(prospect.floor),
      size: number(prospect.size_sqm),
    });
  });

  readonly taxBenefit = computed<string>(() => {
    const amount = this.prospect().monthly_tax_benefit;
    return amount === null ? '—' : moneyFormat(this.languageService.language(), this.currency()).format(amount);
  });

  readonly agency = computed<string>(() => {
    const prospect = this.prospect();
    const t = this.t().panel;
    const parts = [prospect.via_agency ? t.viaAgency : t.noAgency];
    if (prospect.agency_fee !== null) {
      const amount = moneyFormat(this.languageService.language(), this.currency()).format(prospect.agency_fee);
      parts.push(fill(t.agencyFee, {amount}));
    }
    return parts.join(' · ');
  });

  readonly availableFrom = computed<string>(() => {
    const date = this.prospect().available_from;
    return date ? new Intl.DateTimeFormat(this.languageService.language(), {dateStyle: 'medium'}).format(parseDate(date)) : '—';
  });

  readonly contactMethodLabels = computed<Record<number, string>>(() => {
    const t = this.t();
    return Object.fromEntries(this.prospect().contacts.map(c => [c.id, fill(t.panel.contactMethod, {method: t.contactMethods[c.method]})]));
  });

  protected readonly bootstrapStar = bootstrapStar;
  protected readonly bootstrapStarFill = bootstrapStarFill;
}
