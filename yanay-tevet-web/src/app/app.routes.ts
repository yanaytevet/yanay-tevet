import {Routes} from '@angular/router';
import {LayoutComponent} from './layout/layout.component';
import {HomeComponent} from './home/home.component';
import {loggedInGuard} from './common/authentication/logged-in.guard';
import {notLoggedInGuard} from './common/authentication/not-logged-in.guard';
import {hasPermissionGuard} from './common/authentication/has-permission.guard';
import {adminGuard} from './common/authentication/admin.guard';

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
                path: 'genre-trainer',
                loadComponent: () =>
                    import('./genre-trainer/genre-trainer.component').then(m => m.GenreTrainerComponent),
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
            {
                path: 'dream-diary/new',
                loadComponent: () =>
                    import('./dream-diary/dream-diary-entry-form/dream-diary-entry-form.component').then(m => m.DreamDiaryEntryFormComponent),
                canActivate: [hasPermissionGuard('dream_diary')],
            },
            {
                path: 'dream-diary/edit/:id',
                loadComponent: () =>
                    import('./dream-diary/dream-diary-entry-form/dream-diary-entry-form.component').then(m => m.DreamDiaryEntryFormComponent),
                canActivate: [hasPermissionGuard('dream_diary')],
            },
            {
                path: 'japanese',
                loadComponent: () =>
                    import('./japanese/japanese-home/japanese-home.component').then(m => m.JapaneseHomeComponent),
            },
            {
                path: 'japanese/node/:id',
                loadComponent: () =>
                    import('./japanese/japanese-node-detail/japanese-node-detail.component').then(m => m.JapaneseNodeDetailComponent),
            },
            {
                path: 'japanese/ingest',
                loadComponent: () =>
                    import('./japanese/japanese-ingest/japanese-ingest.component').then(m => m.JapaneseIngestComponent),
                canActivate: [adminGuard],
            },
            {
                path: 'japanese/review',
                loadComponent: () =>
                    import('./japanese/japanese-review/japanese-review.component').then(m => m.JapaneseReviewComponent),
                canActivate: [adminGuard],
            },
            {
                path: 'my-dashboard',
                loadComponent: () =>
                    import('./my-dashboard/my-dashboard.component').then(m => m.MyDashboardComponent),
                canActivate: [adminGuard],
            },
            {
                path: 'admin/users',
                loadComponent: () =>
                    import('./admin/user-management/user-management.component').then(m => m.UserManagementComponent),
                canActivate: [adminGuard],
            },
            {
                path: 'apartment-hunt',
                loadComponent: () =>
                    import('./apartment-hunt/projects-list/projects-list.component').then(m => m.ProjectsListComponent),
                canActivate: [hasPermissionGuard('apartment_hunt')],
            },
            {
                path: 'apartment-hunt/projects/new',
                loadComponent: () =>
                    import('./apartment-hunt/project-form/project-form.component').then(m => m.ProjectFormComponent),
                canActivate: [hasPermissionGuard('apartment_hunt')],
            },
            {
                path: 'apartment-hunt/projects/:id/edit',
                loadComponent: () =>
                    import('./apartment-hunt/project-form/project-form.component').then(m => m.ProjectFormComponent),
                canActivate: [hasPermissionGuard('apartment_hunt')],
            },
            {
                path: 'apartment-hunt/projects/:projectId/prospects/new',
                loadComponent: () =>
                    import('./apartment-hunt/prospect-form/prospect-form.component').then(m => m.ProspectFormComponent),
                canActivate: [hasPermissionGuard('apartment_hunt')],
            },
            {
                path: 'apartment-hunt/projects/:projectId/prospects/:id/edit',
                loadComponent: () =>
                    import('./apartment-hunt/prospect-form/prospect-form.component').then(m => m.ProspectFormComponent),
                canActivate: [hasPermissionGuard('apartment_hunt')],
            },
            {
                path: 'apartment-hunt/projects/:id',
                loadComponent: () =>
                    import('./apartment-hunt/project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
                canActivate: [hasPermissionGuard('apartment_hunt')],
            },
            {
                path: 'itinerary-lists',
                loadComponent: () =>
                    import('./itinerary-lists/lists/lists.component').then(m => m.ListsComponent),
                canActivate: [hasPermissionGuard('itinerary_lists')],
            },
            {
                path: 'itinerary-lists/lists/new',
                loadComponent: () =>
                    import('./itinerary-lists/list-form/list-form.component').then(m => m.ListFormComponent),
                canActivate: [hasPermissionGuard('itinerary_lists')],
            },
            {
                path: 'itinerary-lists/lists/:id/edit',
                loadComponent: () =>
                    import('./itinerary-lists/list-form/list-form.component').then(m => m.ListFormComponent),
                canActivate: [hasPermissionGuard('itinerary_lists')],
            },
            {
                path: 'itinerary-lists/lists/:id',
                loadComponent: () =>
                    import('./itinerary-lists/list-detail/list-detail.component').then(m => m.ListDetailComponent),
                canActivate: [hasPermissionGuard('itinerary_lists')],
            },
            {
                path: 'task-management',
                loadComponent: () =>
                    import('./task-management/projects-list/projects-list.component').then(m => m.ProjectsListComponent),
                canActivate: [hasPermissionGuard('task_management')],
            },
            {
                path: 'task-management/projects/new',
                loadComponent: () =>
                    import('./task-management/project-form/project-form.component').then(m => m.ProjectFormComponent),
                canActivate: [hasPermissionGuard('task_management')],
            },
            {
                path: 'task-management/projects/:id/edit',
                loadComponent: () =>
                    import('./task-management/project-form/project-form.component').then(m => m.ProjectFormComponent),
                canActivate: [hasPermissionGuard('task_management')],
            },
            {
                path: 'task-management/projects/:id',
                loadComponent: () =>
                    import('./task-management/project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
                canActivate: [hasPermissionGuard('task_management')],
            },
        ],
    },
];
