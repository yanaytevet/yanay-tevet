import {AfterViewInit, Directive, ElementRef, inject, output} from '@angular/core';
import {DIALOG_DATA} from './dialogs.service';

@Directive()
export abstract class BaseDialogComponent<TInput = void, TOutput = void> implements AfterViewInit {
    data: TInput = inject(DIALOG_DATA);
    closeDialog = output<TOutput | null>();
    private elementRef = inject(ElementRef);

    // Method to emit the result and close the dialog
    public emitClose(result: TOutput | null = null): void {
        this.closeDialog.emit(result);
    }

    ngAfterViewInit(): void {
        this.setInitialFocus();
    }

    private setInitialFocus(): void {
        const element = this.elementRef.nativeElement;

        // Try to focus the first input element
        const inputElement = element.querySelector('input, textarea, select');
        if (inputElement) {
            inputElement.focus();
            return;
        }

        // If no input element, try to focus the confirm button
        const confirmButton = element.querySelector('.accept-btn, [class*="confirm"], app-confirmation-button button');
        if (confirmButton) {
            confirmButton.focus();
            return;
        }

        // If no confirm button, focus the close/cancel button
        const closeButton = element.querySelector('.cancel-btn, [class*="cancel"], [class*="close"]');
        if (closeButton) {
            closeButton.focus();
        }
    }
}
