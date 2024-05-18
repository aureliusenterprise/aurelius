import { Component } from '@angular/core';
import { faProjectDiagram, faServer, faTable, faTag, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext, SortableTableShellConfig } from '@models4insight/components';


interface TableData {
  readonly description: string;
  readonly icon: IconDefinition;
  readonly typeName: string;
}

const modalContext: ModalContext = {
  ...defaultModalContext,
  title: 'Technical context',
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
      'Represents the computing environment on which many data collections can be stored and application processes are run.',
    icon: faServer,
    typeName: 'm4i_system'
  },
  {
    description:
      'Represents a set of datasets, e.g. a database which usually contains multiple tables.',
    icon: faProjectDiagram,
    typeName: 'm4i_collection'
  },
  {
    description:
      'Represents a set of data fields. The most common example of a dataset is a table.',
    icon: faTable,
    typeName: 'm4i_dataset'
  },
  {
    description:
      'Represents a single, indivisible unit of data. The most common example of a field is a column in a table.',
    icon: faTag,
    typeName: 'm4i_field'
  }
];

@Component({
  selector: 'models4insight-technical-context-info-modal',
  templateUrl: 'technical-context-info-modal.component.html',
  styleUrls: ['technical-context-info-modal.component.scss']
})
export class TechnicalContextInfoModalComponent extends AbstractModal {
  readonly modalContext = modalContext;
  readonly tableConfig = tableConfig;
  readonly tableData = tableData;
}
