import {Component, computed, inject, input} from '@angular/core';
import {Currency, RenterProspectSchema} from '../../../generated-files/api/renters-crm';
import {moneyFormat} from '../renters-crm.constants';
import {injectStrings} from '../../shared/i18n/strings';
import {LanguageService} from '../../shared/i18n/language.service';
import {RENTERS_CRM_STRINGS} from '../i18n';

@Component({
  selector: 'app-renter-details-panel',
  standalone: true,
  templateUrl: './renter-details-panel.component.html',
})
export class RenterDetailsPanelComponent {
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(RENTERS_CRM_STRINGS);

  readonly renter = input.required<RenterProspectSchema>();
  readonly currency = input.required<Currency>();

  readonly visitTime = computed<string>(() => {
    const visit = this.renter().visit_time;
    return visit
      ? new Intl.DateTimeFormat(this.languageService.language(), {dateStyle: 'medium', timeStyle: 'short'}).format(new Date(visit))
      : '—';
  });

  readonly agreedRent = computed<string>(() => {
    const amount = this.renter().agreed_rent;
    return amount === null ? '—' : moneyFormat(this.languageService.language(), this.currency()).format(amount);
  });
}
