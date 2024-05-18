import { Component, OnInit } from '@angular/core';
import { faLayerGroup } from '@fortawesome/free-solid-svg-icons';
import { AbstractSelectComponent, defaultControlShellContext, defaultSelectContext, ModalContext, SelectContext, SortableTableShellConfig } from '@models4insight/components';
import { ExemptionScope } from '../../report.service';

export interface ExemptionScopeSelectRow {
  description: string;
  name: string;
  type: ExemptionScope;
}

const exemptionScopeModalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  title: 'Choose a scope'
};

const exemptionScopeTableConfig: SortableTableShellConfig<
  ExemptionScopeSelectRow
> = {
  name: { displayName: 'Scope', description: 'The scope of the exemption' },
  description: {
    displayName: 'Description',
    description: 'The description of the scope'
  }
};

export const exemptionScopeSelectContext: SelectContext = {
  ...defaultSelectContext,
  icon: faLayerGroup,
  label: 'Scope',
  requiredErrorMessage: 'Please select a scope',
  nullInputMessage: 'Please select a scope',
  searchModalContext: exemptionScopeModalContext,
  searchTableConfig: exemptionScopeTableConfig
};

const exemptionScopeSelectData: ExemptionScopeSelectRow[] = [
  {
    type: 'project',
    name: 'This project',
    description: 'This exemption should apply to the whole project'
  },
  {
    type: 'branch',
    name: 'This branch',
    description: 'This exemption should apply to the current branch'
  },
  {
    type: 'version',
    name: 'This version',
    description:
      'This exemption should apply to the current version of the model'
  }
];

@Component({
  selector: 'models4insight-scope-select',
  templateUrl: 'scope-select.component.html',
  styleUrls: ['scope-select.component.scss']
})
export class ScopeSelectComponent
  extends AbstractSelectComponent<ExemptionScopeSelectRow>
  implements OnInit {
  ngOnInit() {
    if (
      this.context === defaultControlShellContext ||
      this.context === defaultSelectContext
    ) {
      this.context = exemptionScopeSelectContext;
    }
    this.data = exemptionScopeSelectData;
    this.displayField = 'name';
    this.select.comparator = this.compareScopeOptions;
  }

  private compareScopeOptions(
    a: ExemptionScopeSelectRow,
    b: ExemptionScopeSelectRow
  ) {
    return a && b ? a.type === b.type : a === b;
  }
}
