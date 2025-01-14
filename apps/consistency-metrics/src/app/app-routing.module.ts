import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { faHome } from '@fortawesome/free-solid-svg-icons';

const routes: Routes = [
  { path: '', redirectTo: '/home/generate', pathMatch: 'full' },
  {
    path: 'home',
    loadChildren: () =>
      import('./home/home.module').then(m => m.HomeModule),
    data: { title: 'Home', icon: faHome }
  },
  // Fallback when no prior route is matched
  { path: '**', redirectTo: '', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
