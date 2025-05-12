import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

const routes: Routes = [
  { path: '', redirectTo: '/search/browse', pathMatch: 'full' },
  {
    path: 'search',
    loadChildren: () =>
      import('./search/search.module').then((m) => m.SearchModule),
    data: { title: 'Search', icon: faSearch, hidden: true },
  },
  // Fallback when no prior route is matched
  { path: '**', redirectTo: '', pathMatch: 'full' },
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {
      scrollPositionRestoration: 'enabled',
    }),
  ],
  exports: [RouterModule],
  providers: [],
})
export class AppRoutingModule {}
