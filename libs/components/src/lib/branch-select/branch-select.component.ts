import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { faCodeBranch, faPlus } from '@fortawesome/free-solid-svg-icons';
import { Branch } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { untilDestroyed } from '@models4insight/utils';
import { isEqual } from 'lodash';
import { Observable } from 'rxjs';
import { defaultControlShellContext } from '../control-shell';
import { CreateBranchModalComponent } from '../create-branch-modal';
import { ModalContext } from '../modal';
import {
  AbstractSelectComponent,
  defaultSelectContext,
  SelectContext,
} from '../select';
import { SortableTableShellConfig } from '../sortable-table-shell';

const branchesModalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  title: 'Choose a branch',
};

const branchesTableConfig: SortableTableShellConfig<Branch> = {
  name: { displayName: 'Branch name', description: 'The name of the branch' },
  description: {
    displayName: 'Description',
    description: 'The description of the branch',
  },
};

export const defaultBranchSelectContext: SelectContext = {
  ...defaultSelectContext,
  icon: faCodeBranch,
  label: 'Branch',
  requiredErrorMessage: 'Please select a branch',
  noDataMessage: 'Please create a new branch',
  nullInputMessage: 'Please select a branch',
  searchModalContext: branchesModalContext,
  searchTableConfig: branchesTableConfig,
};

@Component({
  selector: 'models4insight-branch-select',
  templateUrl: 'branch-select.component.html',
  styleUrls: ['branch-select.component.scss'],
})
export class BranchSelectComponent
  extends AbstractSelectComponent<Branch>
  implements OnInit
{
  readonly faPlus = faPlus;

  isCreatingBranch$: Observable<boolean>;

  @Input() withCreateBranch = false;

  @ViewChild(CreateBranchModalComponent, { static: true })
  private readonly createBranchModal: CreateBranchModalComponent;

  constructor(private readonly branchesService: BranchesService) {
    super();
  }

  ngOnInit() {
    if (
      this.context === defaultControlShellContext ||
      this.context === defaultSelectContext
    ) {
      this.context = defaultBranchSelectContext;
    }
    this.select.comparator = this.compareBranchOptions;
    this.displayField = 'name';

    // Whenever a new branch is created via this component, select the new branch in the control
    this.createBranchModal.submission
      .pipe(untilDestroyed(this))
      .subscribe((branch) => {
        this.control.patchValue(branch);
      });

    // Whenever the list of branches updates, update the options in the select component
    this.branchesService.branches
      .pipe(untilDestroyed(this))
      .subscribe((branches) => (this.select.data = branches));

    this.isCreatingBranch$ = this.branchesService.select('isUpdatingBranch');
  }

  activateModal() {
    this.createBranchModal.activate();
  }

  private compareBranchOptions(a: Branch, b: Branch) {
    return a && b ? a.name === b.name : isEqual(a, b);
  }
}
