import {inject, Injectable, InjectionToken, Injector, Type,} from '@angular/core';
import {Overlay, OverlayConfig, OverlayRef,} from '@angular/cdk/overlay';
import {ComponentPortal} from '@angular/cdk/portal';
import {BaseDialogComponent} from './base-dialog.component';
import {
  ConfirmationDialogComponent,
  ConfirmationDialogInput
} from './common-dialogs/confirmation-dialog/confirmation-dialog.component';
import {
  NotificationDialogComponent,
  NotificationDialogInput
} from './common-dialogs/notification-dialog/notification-dialog.component';
import {
  NumberInputDialogComponent,
  NumberInputDialogInput
} from './common-dialogs/number-input-dialog/number-input-dialog.component';
import {
  TextInputDialogComponent,
  TextInputDialogInput
} from './common-dialogs/text-input-dialog/text-input-dialog.component';
import {
  TextConfirmationDialogComponent,
  TextConfirmationDialogInput
} from './common-dialogs/text-confirmation-dialog/text-confirmation-dialog.component';
import {
  SingleSelectionDialogComponent,
  SingleSelectionDialogInput
} from './common-dialogs/single-selection-dialog/single-selection-dialog.component';
import {
  MultipleSelectionDialogComponent,
  MultipleSelectionDialogInput
} from './common-dialogs/multiple-selection-dialog/multiple-selection-dialog.component';
import {
  RangeDialogComponent,
  RangeDialogInput,
  RangeDialogOutput
} from './common-dialogs/range-dialog/range-dialog.component';
import {DarkModeService} from '../services/dark-mode.service';

export const DIALOG_DATA = new InjectionToken<any>('DIALOG_DATA');

@Injectable({ providedIn: 'root' })
export class DialogService {
  private overlay = inject(Overlay);
  private injector = inject(Injector);
  private darkModeService = inject(DarkModeService);

  open<TInput, TOutput>(
      component: Type<BaseDialogComponent<TInput, TOutput>>,
      data?: TInput,
      widthInPercentiles?: number
  ): Promise<TOutput | null> {
    const overlayRef = this.overlay.create(this.getOverlayConfig(widthInPercentiles));

    const injector = Injector.create({
      parent: this.injector,
      providers: [
        { provide: DIALOG_DATA, useValue: data },
        { provide: OverlayRef, useValue: overlayRef },
      ],
    });

    const portal = new ComponentPortal(component, null, injector);
    const componentRef = overlayRef.attach(portal);
    const instance = componentRef.instance;

    // Set the component's width to 100% to ensure it takes up the full width of the overlay
    if (componentRef.location.nativeElement) {
      componentRef.location.nativeElement.style.width = '100%';
    }

    return new Promise<TOutput | null>((resolve) => {
      instance.closeDialog.subscribe((result: TOutput | null) => {
        resolve(result);
        overlayRef.dispose();
      });

      overlayRef.backdropClick().subscribe(() => {
        resolve(null);
        overlayRef.dispose();
      });

      overlayRef.keydownEvents().subscribe(event => {
        if (event.key === 'Escape') {
          resolve(null);
          overlayRef.dispose();
        }
      });
    });
  }

  private getOverlayConfig(widthInPercentiles?: number): OverlayConfig {
    const isDarkMode = this.darkModeService.darkMode();
    const config: OverlayConfig = {
      hasBackdrop: true,
      backdropClass: isDarkMode ? 'cdk-overlay-black-backdrop' : 'cdk-overlay-dark-backdrop',
      positionStrategy: this.overlay
          .position()
          .global()
          .centerHorizontally()
          .centerVertically(),
    };

    const effectiveWidth = widthInPercentiles ?? 50;
    {
      const isMobile = window.innerWidth <= 768;
      config.width = isMobile ? '95%' : `${effectiveWidth}%`;
    }

    return config;
  }

  public async getBooleanFromConfirmationDialog(data: ConfirmationDialogInput, widthInPercentiles?: number): Promise<boolean> {
    const res = await this.open<ConfirmationDialogInput, boolean>(ConfirmationDialogComponent, data, widthInPercentiles);
    return !!res;
  }

  public async showNotificationDialog(data: NotificationDialogInput, widthInPercentiles?: number): Promise<void> {
    await this.open<NotificationDialogInput, void>(NotificationDialogComponent, data, widthInPercentiles);
  }

  public async getNumberFromInputDialog(data: NumberInputDialogInput, widthInPercentiles?: number): Promise<number | null> {
    return await this.open<NumberInputDialogInput, number | null>(NumberInputDialogComponent, data, widthInPercentiles);
  }

  public async getTextFromInputDialog(data: TextInputDialogInput, widthInPercentiles?: number): Promise<string | null> {
    return await this.open<TextInputDialogInput, string | null>(TextInputDialogComponent, data, widthInPercentiles);
  }

  public async getBooleanFromTextConfirmationDialog(data: TextConfirmationDialogInput, widthInPercentiles?: number): Promise<boolean> {
    const res = await this.open<TextConfirmationDialogInput, boolean>(TextConfirmationDialogComponent, data, widthInPercentiles);
    return !!res;
  }

  public async getValueFromSelectionDialog(data: SingleSelectionDialogInput, widthInPercentiles?: number): Promise<any | null> {
    return await this.open<SingleSelectionDialogInput, any | null>(SingleSelectionDialogComponent, data, widthInPercentiles);
  }

  public async getValuesFromMultipleSelectionDialog(data: MultipleSelectionDialogInput, widthInPercentiles?: number): Promise<any[] | null> {
    return await this.open<MultipleSelectionDialogInput, any[] | null>(MultipleSelectionDialogComponent, data, widthInPercentiles);
  }

  public async getRangeFromRangeDialog(data: RangeDialogInput, widthInPercentiles?: number): Promise<RangeDialogOutput | null> {
    return await this.open<RangeDialogInput, RangeDialogOutput | null>(RangeDialogComponent, data, widthInPercentiles);
  }
}
