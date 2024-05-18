import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ArchimateIconModule, SelectModule } from '@models4insight/components';
import { Modelview2Module } from '@models4insight/modelview2';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { RepositoryModule } from '@models4insight/repository';
import { TranslateModule } from '@ngx-translate/core';
import { ModelExploreRoutingModule } from './model-explore-routing.module';
import { ModelExploreComponent } from './model-explore.component';
import { ModelExploreGuard } from './model-explore.guard';
import { ModelExploreResolver } from './model-explore.resolver';
import { ModelExploreService } from './model-explore.service';

@NgModule({
  imports: [
    CommonModule,
    ArchimateIconModule,
    FontAwesomeModule,
    TranslateModule,
    ModelExploreRoutingModule,
    FormsModule,
    ProjectPermissionModule,
    BranchPermissionModule,
    RepositoryModule,
    SelectModule,
    Modelview2Module
  ],
  declarations: [ModelExploreComponent],
  providers: [ModelExploreGuard, ModelExploreResolver, ModelExploreService]
})
export class ModelExploreModule {}
