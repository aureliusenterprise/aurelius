import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { BranchSelectModule, ConflictResolutionTemplateSelectModule, DescriptionInputModule, ModalModule, ProjectSelectModule } from '@models4insight/components';
import { Modelview2Module } from '@models4insight/modelview2';
import { FeatureModule } from '@models4insight/permissions';
import { RepositoryModule } from '@models4insight/repository';
import { CommitModalComponent } from './commit-modal/commit-modal.component';
import { ModelExploreRoutingModule } from './model-explore-routing.module';
import { ModelExploreComponent } from './model-explore.component';

@NgModule({
  imports: [
    CommonModule,
    ModelExploreRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    Modelview2Module,
    RepositoryModule,
    FeatureModule,
    FontAwesomeModule,
    BranchSelectModule,
    ModalModule,
    ProjectSelectModule,
    ConflictResolutionTemplateSelectModule,
    DescriptionInputModule
  ],
  declarations: [ModelExploreComponent, CommitModalComponent],
  providers: []
})
export class ModelExploreModule {}
