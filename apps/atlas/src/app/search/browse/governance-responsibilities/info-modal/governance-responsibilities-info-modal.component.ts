import { Component } from '@angular/core';
import { faUser, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext, SortableTableShellConfig } from '@models4insight/components';

interface TableData {
  readonly description: string;
  readonly icon: IconDefinition;
  readonly typeName: string;
}

const modalContext: ModalContext = {
  ...defaultModalContext,
  title: 'Data governance organization',
  confirm: null
};

const tableConfig: SortableTableShellConfig<TableData> = {
  icon: {
    displayName: 'Icon',
    description: 'The icon representing the role',
    isNarrow: true,
    isStatic: true
  },
  typeName: {
    displayName: 'Type name',
    description: 'The name of the role',
    isNarrow: true
  },
  description: {
    displayName: 'Description',
    description: 'The definition of the role'
  }
};

const tableData: TableData[] = [
  {
    description:
      'Accountable for the implementation of data management within a data domain.',
    icon: faUser,
    typeName: 'Domain lead'
  },
  {
    description:
      'Responsible for defining data entities within his or her data domain and the effectiveness of related control measures.',
    icon: faUser,
    typeName: 'Data owner'
  },
  {
    description:
      'Responsible for the implementation of data management controls and related initiatives.',
    icon: faUser,
    typeName: 'Data steward'
  }
];

@Component({
  selector: 'models4insight-governance-responsibilities-info-modal',
  templateUrl: 'governance-responsibilities-info-modal.component.html',
  styleUrls: ['governance-responsibilities-info-modal.component.scss']
})
export class GovernanceResponsibilitiesInfoModalComponent extends AbstractModal {
  readonly modalContext = modalContext;
  readonly tableConfig = tableConfig;
  readonly tableData = tableData;
}
