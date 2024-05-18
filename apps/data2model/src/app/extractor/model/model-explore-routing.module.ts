import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ModelExploreComponent } from './model-explore.component';

const routes: Routes = [
    {
        path: '',
        component: ModelExploreComponent,
        data: {
            title: extract('Model Explorer')
        }
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: []
})
export class ModelExploreRoutingModule { }
