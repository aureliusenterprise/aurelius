import { Component, Input, OnInit } from '@angular/core';
import { faBullseye } from '@fortawesome/free-solid-svg-icons';
import { ConflictResolutionTemplateEnum } from '@models4insight/repository';
import {
  AbstractSelectComponent,
  defaultSelectContext,
  SelectContext,
} from '../select';
import { defaultControlShellContext } from '../control-shell';

export interface ConflictResolutionTemplateSelectOption {
  name: string;
  description: string;
  template: ConflictResolutionTemplateEnum;
}

const conflictResolutionTemplateSelectData: ConflictResolutionTemplateSelectOption[] =
  [
    {
      name: 'Replace repository',
      description:
        'Replace the repository head with the new model or source branch',
      template: ConflictResolutionTemplateEnum.UPLOAD_ONLY,
    },
    {
      name: 'Keep repository',
      description: 'De facto nothing changes',
      template: ConflictResolutionTemplateEnum.REPOSITORY_ONLY,
    },
    {
      name: 'Union replace repository',
      description:
        'In case of conflicts, replace the repository with the new model or source branch',
      template: ConflictResolutionTemplateEnum.UNION_UPLOAD,
    },
    {
      name: 'Union keep repository',
      description: 'In case of conflicts, keep the current repository content',
      template: ConflictResolutionTemplateEnum.UNION_REPOSITORY,
    },
    {
      name: 'Manual conflict resolution',
      description: 'Manually resolve each conflict',
      template: ConflictResolutionTemplateEnum.MANUAL,
    },
  ];

const conflictResolutionTemplateSelectContext: SelectContext = {
  icon: faBullseye,
  label: 'Conflict resolution template',
  nullInputMessage: 'Please select a conflict resolution template',
  requiredErrorMessage: 'Please select a conflict resolution template',
  searchModalContext: {
    cancel: 'Close',
    closeOnConfirm: true,
    title: 'Choose a conflict resolution template',
  },
  searchTableConfig: {
    name: {
      displayName: 'Name',
      description: 'The name of the conflict resolution template',
    },
    description: {
      displayName: 'Description',
      description: 'The effect of the conflict resolution template',
    },
  },
};

@Component({
  selector: 'models4insight-conflict-resolution-template-select',
  templateUrl: 'conflict-resolution-template-select.component.html',
  styleUrls: ['conflict-resolution-template-select.component.scss'],
})
export class ConflictResolutionTemplateSelectComponent
  extends AbstractSelectComponent<ConflictResolutionTemplateSelectOption>
  implements OnInit
{
  @Input() allowManual = false;

  ngOnInit() {
    if (
      this.context === defaultControlShellContext ||
      this.context === defaultSelectContext
    ) {
      this.context = conflictResolutionTemplateSelectContext;
    }
    this.data = this.allowManual
      ? conflictResolutionTemplateSelectData
      : conflictResolutionTemplateSelectData.filter(
          ({ template }) => template !== ConflictResolutionTemplateEnum.MANUAL
        );
    this.displayField = 'name';
  }
}
