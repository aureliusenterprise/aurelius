import { Component, Input, OnInit } from '@angular/core';
import {
  ControlShellContext,
  defaultControlShellContext,
  AbstractControlShell,
} from '../control-shell';
import { faCodeBranch } from '@fortawesome/free-solid-svg-icons';

export interface BranchNameInputContext extends ControlShellContext {}

export const defaultBranchNameInputContext: BranchNameInputContext = {
  ...defaultControlShellContext,
  icon: faCodeBranch,
  label: 'Branch name',
  requiredErrorMessage: 'Please provide a branch name',
};

@Component({
  selector: 'models4insight-branch-name-input',
  templateUrl: 'branch-name-input.component.html',
  styleUrls: ['branch-name-input.component.scss'],
})
export class BranchNameInputComponent
  extends AbstractControlShell
  implements OnInit
{
  @Input() inputClasses: string[] = [];

  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultBranchNameInputContext;
    }
  }
}
