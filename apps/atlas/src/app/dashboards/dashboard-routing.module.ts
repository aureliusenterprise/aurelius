import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { Shell } from "@models4insight/shell";
import { DomainsComponent } from "./domains/domains.component";

const childRoutes: Routes = [
    {
        path: '',
        pathMatch: 'full',
        redirectTo: 'domains'
    },
    {
        path: 'domains',
        component: DomainsComponent
    },
    {
        path: '**',
        pathMatch: 'full',
        redirectTo: 'domains'
    }
]
const routes: Routes = [
    Shell.childRoutes([
        {
            path: '',
            component: DomainsComponent,
            children: childRoutes
        }
    ])
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class DashboardRoutingModule { }

