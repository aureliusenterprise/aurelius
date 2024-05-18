import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { BranchSelectModule, ProjectSelectModule, ProvenanceSelectModule } from '@models4insight/components';
import { GenerateReportRoutingModule } from './generate-report-routing.module';
import { GenerateReportComponent } from './generate-report.component';
import { GenerateReportService } from './generate-report.service';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    FormsModule,
    ReactiveFormsModule,
    GenerateReportRoutingModule,
    ProjectSelectModule,
    BranchSelectModule,
    ProvenanceSelectModule
  ],
  declarations: [GenerateReportComponent],
  providers: [GenerateReportService]
})
export class GenerateReportModule {}
