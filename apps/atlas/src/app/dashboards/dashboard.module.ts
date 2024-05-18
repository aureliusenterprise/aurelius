import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { DashboardRoutingModule } from "./dashboard-routing.module";
import { CardDashboardComponent } from "./domains/cards/cards-dashboard.component";
import { DomainsComponent } from "./domains/domains.component";
@NgModule({
    declarations: [DomainsComponent, CardDashboardComponent],
    imports: [
        CommonModule,
        FontAwesomeModule,
        DashboardRoutingModule
    ]
})
export class DashboardModule { }
