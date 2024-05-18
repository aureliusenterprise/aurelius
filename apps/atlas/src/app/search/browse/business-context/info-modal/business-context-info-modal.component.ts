import { Component } from '@angular/core';
import { faProjectDiagram, faTable, faTag, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext, SortableTableShellConfig } from '@models4insight/components';

interface TableData {
  readonly description: string;
  readonly icon: IconDefinition;
  readonly typeName: string;
}

const modalContext: ModalContext = {
  ...defaultModalContext,
  title: 'Business context',
  confirm: null
};

const tableConfig: SortableTableShellConfig<TableData> = {
  icon: {
    displayName: 'Icon',
    description: 'The icon representing the entity type',
    isNarrow: true,
    isStatic: true
  },
  typeName: {
    displayName: 'Type name',
    description: 'The name of the entity type',
    isNarrow: true
  },
  description: {
    displayName: 'Description',
    description: 'The definition of the entity type'
  }
};

const tableData: TableData[] = [
  {
    description:
      'Represents departments, business units and process owners accountable for data due to their accountability in the organization.',
    icon: faProjectDiagram,
    typeName: 'm4i_data_domain'
  },
  {
    description:
      'Represents the meaning and ownership of business process data artifacts that are used in a specific data domain.',
    icon: faTable,
    typeName: 'm4i_data_entity'
  },
  {
    description:
      'Represents the meaning and ownership of an atomic data point that is part of a specific data entity.',
    icon: faTag,
    typeName: 'm4i_data_attribute'
  }
];

@Component({
  selector: 'models4insight-business-context-info-modal',
  templateUrl: 'business-context-info-modal.component.html',
  styleUrls: ['business-context-info-modal.component.scss']
})
export class BusinessContextInfoModalComponent extends AbstractModal {
  readonly modalContext = modalContext;
  readonly tableConfig = tableConfig;
  readonly tableData = tableData;
}
