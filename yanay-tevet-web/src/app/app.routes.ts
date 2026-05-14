import {Routes} from '@angular/router';
import {LayoutComponent} from './layout/layout.component';
import {HomeComponent} from './home/home.component';
import {loggedInGuard} from './common/authentication/logged-in.guard';
import {notLoggedInGuard} from './common/authentication/not-logged-in.guard';
import {hasPermissionGuard} from './common/authentication/has-permission.guard';

export const routes: Routes = [
    // Login
    {
        path: 'login',
        loadComponent: () =>
            import('./login/login.component').then(m => m.LoginComponent),
        canActivate: [notLoggedInGuard],
    },
    // All pages under single layout
    {
        path: '',
        component: LayoutComponent,
        children: [
            {
                path: '',
                component: HomeComponent,
                pathMatch: 'full',
            },
            {
                path: 'faq',
                loadComponent: () =>
                    import('./faq/faq.component').then(m => m.FaqComponent),
            },
            {
                path: 'terms',
                loadComponent: () =>
                    import('./terms/terms.component').then(m => m.TermsComponent),
            },
            {
                path: 'privacy',
                loadComponent: () =>
                    import('./privacy/privacy.component').then(m => m.PrivacyComponent),
            },
            {
                path: 'contact',
                loadComponent: () =>
                    import('./contact/contact.component').then(m => m.ContactComponent),
            },
            {
                path: 'example-form',
                loadComponent: () =>
                    import('./example/example-form/example-form.component').then(m => m.ExampleFormComponent),
                canActivate: [loggedInGuard],
            },
            {
                path: 'example-table',
                loadComponent: () =>
                    import('./example/example-table/example-table.component').then(m => m.ExampleTableComponent),
                canActivate: [loggedInGuard],
            },
            {
                path: 'example-dialogs',
                loadComponent: () =>
                    import('./example/example-dialogs/example-dialogs.component').then(m => m.ExampleDialogsComponent),
                canActivate: [loggedInGuard],
            },
            {
                path: 'example-websockets',
                loadComponent: () =>
                    import('./example/example-websocket/example-websocket.component').then(m => m.ExampleWebsocketComponent),
                canActivate: [loggedInGuard],
            },
            {
                path: 'example-files',
                loadComponent: () =>
                    import('./example/example-files/example-files.component').then(m => m.ExampleFilesComponent),
                canActivate: [loggedInGuard],
            },
            {
                path: 'user-settings',
                loadComponent: () =>
                    import('./user-settings/user-settings-page').then(m => m.UserSettingsPage),
                canActivate: [loggedInGuard],
            },
            {
                path: 'dream-diary',
                loadComponent: () =>
                    import('./dream-diary/dream-diary.component').then(m => m.DreamDiaryComponent),
                canActivate: [hasPermissionGuard('dream_diary')],
            },
        ],
    },
];
