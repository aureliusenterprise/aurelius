import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { faHome, faQuestionCircle } from '@fortawesome/free-solid-svg-icons';

const routes: Routes = [
  { path: '', redirectTo: '/home/upload', pathMatch: 'full' },
  {
    path: 'home',
    loadChildren: () =>
      import('./extractor/extractor.module').then(m => m.ExtractorModule),
    data: { title: 'Home', icon: faHome }
  },
  {
    path: 'about',
    loadChildren: () => import('./about/about.module').then(m => m.AboutModule),
    data: { title: 'About', icon: faQuestionCircle }
  },
  // Fallback when no prior route is matched
  { path: '**', redirectTo: '', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { relativeLinkResolution: 'legacy' })],
  exports: [RouterModule],
  providers: []
})
export class AppRoutingModule {}
