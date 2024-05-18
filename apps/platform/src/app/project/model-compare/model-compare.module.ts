import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { SelectModule } from '@models4insight/components';
import { Modelview2Module } from '@models4insight/modelview2';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { RepositoryModule } from '@models4insight/repository';
import { TranslateModule } from '@ngx-translate/core';
import { ModelCompareRoutingModule } from './model-compare-routing.module';
import { ModelCompareComponent } from './model-compare.component';
import { ModelCompareGuard } from './model-compare.guard';
import { ModelCompareResolver } from './model-compare.resolver';
import { ModelCompareService } from './model-compare.service';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    TranslateModule,
    ModelCompareRoutingModule,
    FormsModule,
    Modelview2Module,
    ProjectPermissionModule,
    BranchPermissionModule,
    RepositoryModule,
    SelectModule
  ],
  declarations: [ModelCompareComponent],
  providers: [ModelCompareGuard, ModelCompareResolver, ModelCompareService]
})
export class ModelCompareModule {}
