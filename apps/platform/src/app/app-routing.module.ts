import { NgModule } from '@angular/core';
import { ExtraOptions, RouterModule, Routes } from '@angular/router';
import { faHome, faProjectDiagram, faQuestionCircle } from '@fortawesome/free-solid-svg-icons';

export const routingConfiguration: ExtraOptions = {
    paramsInheritanceStrategy: 'always',
};

const routes: Routes = [
  { path: '', redirectTo: '/home/welcome', pathMatch: 'full' },
  {
    path: 'home',
    loadChildren: () => import('./home/home.module').then(m => m.HomeModule),
    data: { title: 'Home', icon: faHome }
  },
  {
    path: 'projects',
    loadChildren: () =>
      import('./projects/projects.module').then(m => m.ProjectsModule),
    data: { title: 'Projects', icon: faProjectDiagram }
  },
  {
    path: 'about',
    loadChildren: () => import('./about/about.module').then(m => m.AboutModule),
    data: { title: 'About', icon: faQuestionCircle }
  },
  {
    path: 'project',
    loadChildren: () =>
      import('./project/project.module').then(m => m.ProjectModule),
    data: { hidden: true }
  },
  // Fallback when no prior route is matched
  { path: '**', redirectTo: '', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  providers: []
})
export class AppRoutingModule {}
