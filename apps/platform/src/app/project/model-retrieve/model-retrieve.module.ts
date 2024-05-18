import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ContextMenuModule, ControlShellModule, SortableTableShellModule, DatePickerModule, SimpleSearchInputModule, CompareModalModule } from '@models4insight/components';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import { BranchesTableContextMenuComponent } from './branches-table/branches-table-context-menu/branches-table-context-menu.component';
import { BranchesTableComponent } from './branches-table/branches-table.component';
import { ModelRetrieveRoutingModule } from './model-retrieve-routing.module';
import { ModelRetrieveComponent } from './model-retrieve.component';
import { ModelRetrieveGuard } from './model-retrieve.guard';
import { ModelRetrieveResolver } from './model-retrieve.resolver';
import { ModelRetrieveService } from './model-retrieve.service';
import { ProvenanceTableComponent } from './provenance-table/provenance-table.component';
import { ProvenanceTableContextMenuComponent } from './provenance-table/provenance-table-context-menu/provenance-table-context-menu.component';

@NgModule({
  imports: [
    CommonModule,
    ControlShellModule,
    DatePickerModule,
    FontAwesomeModule,
    TranslateModule,
    ModelRetrieveRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    ProjectPermissionModule,
    BranchPermissionModule,
    ContextMenuModule,
    SortableTableShellModule,
    SimpleSearchInputModule,
  ],
  declarations: [
    ModelRetrieveComponent,
    BranchesTableComponent,
    BranchesTableContextMenuComponent,
    ProvenanceTableComponent,
    ProvenanceTableContextMenuComponent
  ],
  providers: [ModelRetrieveGuard, ModelRetrieveResolver, ModelRetrieveService]
})
export class ModelRetrieveModule {}
