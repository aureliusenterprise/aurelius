import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell } from '@models4insight/shell';
import { CardsComponent } from './components/cards/cards.component';

const routes: Routes = [
  Shell.childRoutes(
    [
      {
        path: '',
        component: CardsComponent,
        data: { title: 'Index', hidden: true },
      },
    ],
    false
  ),
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
