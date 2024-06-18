import { Component, OnInit } from '@angular/core';
import { faCalendarAlt } from '@fortawesome/free-solid-svg-icons';
import { ModelProvenance } from '@models4insight/repository';
import { defaultControlShellContext } from '../control-shell';
import { ModalContext } from '../modal';
import {
  AbstractSelectComponent,
  defaultSelectContext,
  SelectContext,
} from '../select';
import { SortableTableShellConfig } from '../sortable-table-shell';

const provenanceModalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  title: 'Choose a version',
};

const provenanceTableConfig: SortableTableShellConfig<ModelProvenance> = {
  start_date: {
    displayName: 'Timestamp',
    description: 'The time at which the version was committed',
    isTimestamp: true,
  },
  start_user: {
    displayName: 'User',
    description: 'The name of the user who committed the version',
  },
  comment: {
    displayName: 'Description',
    description: 'A description of the committed model',
  },
};

const defaultProvenanceSelectContext: SelectContext = {
  ...defaultSelectContext,
  icon: faCalendarAlt,
  isTimestamp: true,
  label: 'Version',
  requiredErrorMessage: 'Please select a version',
  nullInputMessage: 'Please select a version',
  searchModalContext: provenanceModalContext,
  searchTableConfig: provenanceTableConfig,
};

@Component({
  selector: 'models4insight-provenance-select',
  templateUrl: 'provenance-select.component.html',
  styleUrls: ['provenance-select.component.scss'],
})
export class ProvenanceSelectComponent
  extends AbstractSelectComponent<ModelProvenance>
  implements OnInit
{
  ngOnInit() {
    if (
      this.context === defaultControlShellContext ||
      this.context === defaultSelectContext
    ) {
      this.context = defaultProvenanceSelectContext;
    }
    this.displayField = 'start_date';
  }
}
