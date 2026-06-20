import {Routes} from '@angular/router';
import {HomeSweetHomeComponent} from './home-sweet-home.component';

export const HOME_SWEET_HOME_ROUTES: Routes = [
  {
    path: '',
    component: HomeSweetHomeComponent,
    children: [
      {
        path: '',
        redirectTo: 'apartment-hunt',
        pathMatch: 'full',
      },
      // Apartment Hunt sub-app
      {
        path: 'apartment-hunt',
        loadComponent: () =>
          import('../apartment-hunt/projects-list/projects-list.component').then(m => m.ProjectsListComponent),
      },
      {
        path: 'apartment-hunt/projects/new',
        loadComponent: () =>
          import('../apartment-hunt/project-form/project-form.component').then(m => m.ProjectFormComponent),
      },
      {
        path: 'apartment-hunt/projects/:id/edit',
        loadComponent: () =>
          import('../apartment-hunt/project-form/project-form.component').then(m => m.ProjectFormComponent),
      },
      {
        path: 'apartment-hunt/projects/:projectId/prospects/new',
        loadComponent: () =>
          import('../apartment-hunt/prospect-form/prospect-form.component').then(m => m.ProspectFormComponent),
      },
      {
        path: 'apartment-hunt/projects/:projectId/prospects/:id/edit',
        loadComponent: () =>
          import('../apartment-hunt/prospect-form/prospect-form.component').then(m => m.ProspectFormComponent),
      },
      {
        path: 'apartment-hunt/projects/:id',
        loadComponent: () =>
          import('../apartment-hunt/project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
      },
      // Villa Villekulla sub-app (placeholder)
      {
        path: 'villa-villekulla',
        loadComponent: () =>
          import('./villa-villekulla/villa-villekulla.component').then(m => m.VillaVillekullaComponent),
      },
      // Renters CRM sub-app (placeholder)
      {
        path: 'renters-crm',
        loadComponent: () =>
          import('./renters-crm/renters-crm.component').then(m => m.RentersCrmComponent),
      },
    ],
  },
];
