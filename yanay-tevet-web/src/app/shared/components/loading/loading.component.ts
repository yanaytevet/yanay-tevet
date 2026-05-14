import {Component, computed, OnDestroy, OnInit, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  heroSparkles,
  heroBolt,
  heroBookOpen,
  heroEye,
  heroShieldCheck,
  heroBeaker,
  heroFire,
  heroStar,
} from '@ng-icons/heroicons/outline';

const LOADING_TEXTS = [
  'Loading...',
  'Hang tight...',
  'Almost there...',
  'Fetching data...',
  'Just a moment...',
  'Working on it...',
  'Please wait...',
];

const ICONS = [
  'heroSparkles',
  'heroBolt',
  'heroBookOpen',
  'heroEye',
  'heroShieldCheck',
  'heroBeaker',
  'heroFire',
  'heroStar',
];

@Component({
  selector: 'app-loading',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({heroSparkles, heroBolt, heroBookOpen, heroEye, heroShieldCheck, heroBeaker, heroFire, heroStar})],
  templateUrl: './loading.component.html',
  styleUrl: './loading.component.css',
})
export class LoadingComponent implements OnInit, OnDestroy {
  readonly currentIconIndex = signal(0);
  readonly iconVisible = signal(true);

  readonly loadingText = LOADING_TEXTS[Math.floor(Math.random() * LOADING_TEXTS.length)];
  readonly textChars = this.loadingText.split('');

  readonly currentIcon = computed(() => ICONS[this.currentIconIndex() % ICONS.length]);

  private iconTimer?: ReturnType<typeof setInterval>;

  ngOnInit() {
    this.iconTimer = setInterval(() => {
      this.iconVisible.set(false);
      setTimeout(() => {
        this.currentIconIndex.update(i => (i + 1) % ICONS.length);
        this.iconVisible.set(true);
      }, 300);
    }, 2000);
  }

  ngOnDestroy() {
    clearInterval(this.iconTimer);
  }
}
