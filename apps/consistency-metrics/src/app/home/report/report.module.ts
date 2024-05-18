import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ContextMenuModule, DescriptionInputModule, ModalModule, SelectModule, SortableTableShellModule } from '@models4insight/components';
import { BokehChartModule, CopyModule, HoldableModule } from '@models4insight/directives';
import { Modelview2Module } from '@models4insight/modelview2';
import { AddExemptionModalComponent } from './add-exemption-modal/add-exemption-modal.component';
import { ScopeSelectComponent } from './add-exemption-modal/scope-select/scope-select.component';
import { CopyButtonComponent } from './copy-button/copy-button.component';
import { ExemptionsService } from './exemptions.service';
import { ReportContextMenuComponent } from './report-context-menu/report-context-menu.component';
import { ReportExemptionsContextMenuComponent } from './report-exemptions/report-exemptions-context-menu/report-exemptions-context-menu.component';
import { ReportExemptionsComponent } from './report-exemptions/report-exemptions.component';
import { ReportExemptionsService } from './report-exemptions/report-exemptions.service';
import { ReportMetricComponent } from './report-metric/report-metric.component';
import { ReportRoutingModule } from './report-routing.module';
import { ReportTableComponent } from './report-table/report-table.component';
import { ReportComponent } from './report.component';
import { ReportResolver } from './report.resolver';
import { ReportService } from './report.service';
import { ViolationsService } from './violations.service';

@NgModule({
  imports: [
    BokehChartModule,
    CommonModule,
    ContextMenuModule,
    CopyModule,
    DescriptionInputModule, 
    FontAwesomeModule,
    HoldableModule,
    ModalModule,
    Modelview2Module,
    ReportRoutingModule,
    SelectModule,
    SortableTableShellModule
  ],
  declarations: [
    AddExemptionModalComponent,
    CopyButtonComponent,
    ReportComponent,
    ReportContextMenuComponent,
    ReportExemptionsComponent,
    ReportExemptionsContextMenuComponent,
    ReportMetricComponent,
    ReportTableComponent,
    ScopeSelectComponent
  ],
  providers: [ExemptionsService, ReportExemptionsService, ReportResolver, ReportService, ViolationsService]
})
export class ReportModule {}
