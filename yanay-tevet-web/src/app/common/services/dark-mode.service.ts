import {effect, inject, Injectable, RendererFactory2, signal} from '@angular/core';
import {DOCUMENT} from '@angular/common';

@Injectable({
    providedIn: 'root'
})
export class DarkModeService {
    private rendererFactory = inject(RendererFactory2);
    private renderer = this.rendererFactory.createRenderer(null, null);
    private document = inject(DOCUMENT);

    darkMode = signal<boolean>(
        JSON.parse(localStorage.getItem('darkMode') ?? 'false')
    );

    constructor() {
        effect(() => {
            localStorage.setItem('darkMode', JSON.stringify(this.darkMode()));
            const htmlElement = this.document.documentElement;
            if (this.darkMode()) {
                this.renderer.addClass(htmlElement, 'dark');
            } else {
                this.renderer.removeClass(htmlElement, 'dark');
            }
        });
    }


    toggleDarkMode() {
        this.darkMode.set(!this.darkMode());
    }
}

