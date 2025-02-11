import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { QuickviewModule } from '@models4insight/components';
import {
  DynamicComponentModule,
  HoldableModule,
} from '@models4insight/directives';
import { TranslateModule } from '@ngx-translate/core';
import { GovernanceQualityCardModule } from '../cards/gov-quality/governance-quality-card.module';
import { AttributeEditorComponent } from './attribute/attribute-editor.component';
import { CollectionEditorComponent } from './collection/collection-editor.component';
import { ClassificationsInputModule } from './components/classifications-input/classifications-input.module';
import { RelationshipsInputModule } from './components/relationships-input/relationships-input.module';
import { DatasetEditorComponent } from './dataset/dataset-editor.component';
import { DomainEditorComponent } from './domain/domain-editor.component';
import { EditorComponent } from './editor.component';
import { EntityEditorComponent } from './entity/entity-editor.component';
import { FieldEditorComponent } from './field/field-editor.component';
import { GovernanceQualityEditorComponent } from './gov-quality/gov-quality-editor.component';
import { PersonEditorComponent } from './person/person-editor.component';
import { ProcessEditorComponent } from './process/process-editor.component';
import { SystemEditorComponent } from './system/system-editor.component';
import { TypeSelectModule } from './type-select/type-select.module';
import { GovQualityDisplayComponent } from './components/gov-quality-display/gov-quality-display.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { KeycloakRolePermissionModule } from '@models4insight/permissions';

@NgModule({
  imports: [
    CommonModule,
    ClassificationsInputModule,
    DynamicComponentModule,
    FormsModule,
    HoldableModule,
    QuickviewModule,
    ReactiveFormsModule,
    RelationshipsInputModule,
    TranslateModule,
    TypeSelectModule,
    GovernanceQualityCardModule,
    FontAwesomeModule,
    KeycloakRolePermissionModule,
  ],
  declarations: [
    EditorComponent,
    AttributeEditorComponent,
    CollectionEditorComponent,
    DatasetEditorComponent,
    DomainEditorComponent,
    EntityEditorComponent,
    FieldEditorComponent,
    GovernanceQualityEditorComponent,
    PersonEditorComponent,
    ProcessEditorComponent,
    SystemEditorComponent,
    GovQualityDisplayComponent,
  ],
  exports: [EditorComponent],
})
export class EditorModule {}
