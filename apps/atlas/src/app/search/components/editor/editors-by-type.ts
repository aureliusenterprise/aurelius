import { AttributeEditorComponent } from './attribute/attribute-editor.component';
import { CollectionEditorComponent } from './collection/collection-editor.component';
import { DatasetEditorComponent } from './dataset/dataset-editor.component';
import { DomainEditorComponent } from './domain/domain-editor.component';
import { EntityEditorComponent } from './entity/entity-editor.component';
import { FieldEditorComponent } from './field/field-editor.component';
import { GovernanceQualityEditorComponent } from './gov-quality/gov-quality-editor.component';
import { PersonEditorComponent } from './person/person-editor.component';
import { ProcessEditorComponent } from './process/process-editor.component';
import { SystemEditorComponent } from './system/system-editor.component';

export type Editor =
  | AttributeEditorComponent
  | CollectionEditorComponent
  | DatasetEditorComponent
  | DomainEditorComponent
  | EntityEditorComponent
  | FieldEditorComponent
  | GovernanceQualityEditorComponent
  | PersonEditorComponent
  | ProcessEditorComponent
  | SystemEditorComponent;

export const editorsByType = {
  m4i_data_attribute: AttributeEditorComponent,
  m4i_collection: CollectionEditorComponent,
  m4i_dataset: DatasetEditorComponent,
  m4i_data_domain: DomainEditorComponent,
  m4i_data_entity: EntityEditorComponent,
  m4i_field: FieldEditorComponent,
  m4i_generic_process: ProcessEditorComponent,
  m4i_data_quality: GovernanceQualityEditorComponent,
  m4i_gov_data_quality: GovernanceQualityEditorComponent,
  m4i_person: PersonEditorComponent,
  m4i_system: SystemEditorComponent,
};
