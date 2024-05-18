import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TooltipModule } from '@models4insight/directives';
import { KeycloakRolePermissionModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import { BreadCrumbsModule } from '../components/bread-crumbs/bread-crumbs.module';
import { ClassificationsListModule } from '../components/classifications-list/classifications-list.module';
import { EditorModule } from '../components/editor/editor.module';
import { EntityTypeNameModule } from '../components/entity-type-name/entity-type-name.module';
import { TermModule } from '../components/term/term.module';
import { AttributeDetailsModule } from './attribute/attribute-details.module';
import { CollectionDetailsModule } from './collection/collection-details.module';
import { DatasetDetailsModule } from './dataset/dataset-details.module';
import { DefaultDetailsModule } from './default/default-details.module';
import { DetailsRoutingModule } from './details-routing.module';
import { DetailsComponent } from './details.component';
import { DetailsResolver } from './details.resolver';
import { DomainDetailsModule } from './domain/domain-details.module';
import { EntityDetailsModule } from './entity/entity-details.module';
import { FieldDetailsModule } from './field/field-details.module';
import { GovQualityDetailsModule } from './gov-quality/gov-quality-details.module';
import { PersonDetailsModule } from './person/person-details.module';
import { ProcessDetailsModule } from './process/process-details.module';
import { SystemDetailsModule } from './system/system-details.module';

@NgModule({
  declarations: [DetailsComponent],
  imports: [
    CommonModule,
    DomainDetailsModule,
    EntityDetailsModule,
    AttributeDetailsModule,
    FieldDetailsModule,
    DatasetDetailsModule,
    CollectionDetailsModule,
    SystemDetailsModule,
    PersonDetailsModule,
    ProcessDetailsModule,
    DefaultDetailsModule,
    GovQualityDetailsModule,
    FontAwesomeModule,
    TranslateModule.forChild(),
    TooltipModule,
    ClassificationsListModule,
    TermModule,
    BreadCrumbsModule,
    EditorModule,
    DetailsRoutingModule,
    KeycloakRolePermissionModule,
    EntityTypeNameModule,
  ],
  providers: [DetailsResolver],
})
export class DetailsModule {}
