import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ModalModule, SimpleSearchInputModule, SortableTableShellModule } from '@models4insight/components';
import { TranslateModule } from '@ngx-translate/core';
import { BrowseComponent } from './browse.component';
import { BusinessContextComponent } from './business-context/business-context.component';
import { BusinessContextInfoModalComponent } from './business-context/info-modal/business-context-info-modal.component';
import { GovernanceResponsibilitiesComponent } from './governance-responsibilities/governance-responsibilities.component';
import { GovernanceResponsibilitiesInfoModalComponent } from './governance-responsibilities/info-modal/governance-responsibilities-info-modal.component';
import { TechnicalContextInfoModalComponent } from './technical-context/info-modal/technical-context-info-modal.component';
import { TechnicalContextComponent } from './technical-context/technical-context.component';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    ModalModule,
    SimpleSearchInputModule,
    SortableTableShellModule,
    TranslateModule
  ],
  declarations: [
    BrowseComponent,
    BusinessContextComponent,
    BusinessContextInfoModalComponent,
    GovernanceResponsibilitiesComponent,
    GovernanceResponsibilitiesInfoModalComponent,
    TechnicalContextComponent,
    TechnicalContextInfoModalComponent
  ]
})
export class BrowseModule {}
