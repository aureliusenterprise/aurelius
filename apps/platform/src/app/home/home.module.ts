import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { CreateProjectModalModule, SortableTableModule } from '@models4insight/components';
import { RepositoryModule } from '@models4insight/repository';
import { TranslateModule } from '@ngx-translate/core';
import { AnalyticsComponent } from './analytics/analytics.component';
import { HomeRoutingModule } from './home-routing.module';
import { HomeComponent } from './home.component';
import { InsightsComponent } from './insights/insights.component';
import { ModelingComponent } from './modeling/modeling.component';
import { MonitoringComponent } from './monitoring/monitoring.component';
import { WelcomeComponent } from './welcome/welcome.component';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    TranslateModule,
    RepositoryModule,
    FormsModule,
    ReactiveFormsModule,
    HomeRoutingModule,
    CreateProjectModalModule,
    SortableTableModule
  ],
  declarations: [
    AnalyticsComponent,
    HomeComponent,
    InsightsComponent,
    ModelingComponent,
    MonitoringComponent,
    WelcomeComponent
  ],
  providers: []
})
export class HomeModule {}
