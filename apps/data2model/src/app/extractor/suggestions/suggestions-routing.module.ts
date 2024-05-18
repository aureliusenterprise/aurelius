import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { SuggestionsComponent } from './suggestions.component';

const routes: Routes = [
  {
    path: '',
    component: SuggestionsComponent,
    data: {
      title: extract('Suggestions')
    }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class SuggestionsRoutingModule {}
