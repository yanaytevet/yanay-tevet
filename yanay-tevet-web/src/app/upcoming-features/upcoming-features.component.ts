import { Component } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
  bootstrapPeopleFill,
  bootstrapJournalBookmarkFill,
  bootstrapLayoutTextWindowReverse,
  bootstrapLightningChargeFill,
  bootstrapRobot,
} from '@ng-icons/bootstrap-icons';

interface UpcomingFeature {
  icon: string;
  title: string;
  description: string;
}

@Component({
  selector: 'app-upcoming-features',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './upcoming-features.component.html',
  viewProviders: [provideIcons({
    bootstrapPeopleFill,
    bootstrapJournalBookmarkFill,
    bootstrapLayoutTextWindowReverse,
    bootstrapLightningChargeFill,
    bootstrapRobot,
  })],
})
export class UpcomingFeaturesComponent {
  readonly features: UpcomingFeature[] = [
    {
      icon: 'bootstrapPeopleFill',
      title: 'More coming soon',
      description: 'We\'re working on new features. Check back soon.',
    },
  ];
}
