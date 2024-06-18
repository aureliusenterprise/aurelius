import { Component, Input, OnInit } from '@angular/core';
import { faUserShield } from '@fortawesome/free-solid-svg-icons';
import { AuthenticationService } from '@models4insight/authentication';
import { ProjectPermissionService } from '@models4insight/permissions';
import { PermissionLevel } from '@models4insight/repository';
import {
  ProjectMembersService,
  ProjectService,
} from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest, Observable, ReplaySubject } from 'rxjs';
import { map, shareReplay, switchMap, withLatestFrom } from 'rxjs/operators';
import { defaultControlShellContext } from '../control-shell';
import {
  AbstractSelectComponent,
  defaultSelectContext,
  Select,
  SelectContext,
} from '../select';

export interface PermissionSelectOption {
  description: string;
  name: string;
  level: PermissionLevel;
}

const permissionSelectOptionsByPermissionLevel: Dictionary<PermissionSelectOption> =
  {
    [PermissionLevel.OWNER]: {
      name: 'Owner',
      description: 'Can access all project functions',
      level: PermissionLevel.OWNER,
    },
    [PermissionLevel.MAINTAINER]: {
      name: 'Maintainer',
      description: 'Cannot delete the project, or assign new project owners',
      level: PermissionLevel.MAINTAINER,
    },
    [PermissionLevel.CONTRIBUTOR]: {
      name: 'Contributor',
      description: 'Cannot access the project settings',
      level: PermissionLevel.CONTRIBUTOR,
    },
    [PermissionLevel.MODEL_USER]: {
      name: 'Model user',
      description:
        'Can retrieve models, but cannot commit new versions or move branches',
      level: PermissionLevel.MODEL_USER,
    },
    [PermissionLevel.BUSINESS_USER]: {
      name: 'Business user',
      description: 'Can access the model explorer',
      level: PermissionLevel.BUSINESS_USER,
    },
  };

const permissionSelectOptions = Object.values(
  permissionSelectOptionsByPermissionLevel
);

const permissionSelectContext: SelectContext = {
  icon: faUserShield,
  inputClasses: ['is-small'],
  nullInputMessage: 'Please select a permission level',
  requiredErrorMessage: 'Please select a permission level',
  searchModalContext: {
    cancel: 'Close',
    closeOnConfirm: true,
    title: 'Choose a permission level',
  },
  searchTableConfig: {
    name: {
      displayName: 'Name',
      description: 'The name of the permission level',
    },
    description: {
      displayName: 'Description',
      description: 'The effect of the permission level',
    },
  },
};

@Component({
  selector: 'models4insight-permission-select',
  templateUrl: 'permission-select.component.html',
  styleUrls: ['permission-select.component.scss'],
})
export class PermissionSelectComponent
  extends AbstractSelectComponent<PermissionSelectOption>
  implements OnInit
{
  readonly permissionSelectContext = permissionSelectContext;

  readonly faUserShield = faUserShield;

  data$: Observable<PermissionSelectOption[]>;
  isDisabled$: Observable<boolean>;

  private readonly user$ = new ReplaySubject<string>();

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly projectService: ProjectService,
    private readonly projectMembersService: ProjectMembersService,
    private readonly projectPermissionService: ProjectPermissionService
  ) {
    super();
  }

  ngOnInit() {
    if (
      this.context === defaultControlShellContext ||
      this.context === defaultSelectContext
    ) {
      this.context = permissionSelectContext;
    }
    const select = new Select(true);

    this.control = select;
    this.displayField = 'name';

    const userPermissionLevel$ = this.user$.pipe(
      switchMap((user) =>
        this.projectMembersService.selectMemberPermissions(user)
      ),
      shareReplay()
    );

    this.isDisabled$ = combineLatest([
      this.user$,
      userPermissionLevel$,
      this.authenticationService.select(['credentials', 'username']),
      this.projectPermissionService.checkPermission(PermissionLevel.OWNER),
    ]).pipe(
      map(
        ([user, userPermission, currentUser, isOwner]) =>
          currentUser === user ||
          (userPermission === PermissionLevel.OWNER && !isOwner)
      ),
      shareReplay()
    );

    this.data$ = combineLatest([
      this.projectPermissionService.checkPermission(PermissionLevel.OWNER),
      this.isDisabled$,
    ]).pipe(
      map(([isOwner, isDisabled]) =>
        permissionSelectOptions.filter((option) => {
          const minPermissionLevel =
            isOwner || isDisabled
              ? PermissionLevel.OWNER
              : PermissionLevel.MAINTAINER;
          return option.level >= minPermissionLevel;
        })
      )
    );

    userPermissionLevel$
      .pipe(
        map(
          (userPermission) =>
            permissionSelectOptionsByPermissionLevel[userPermission]
        ),
        untilDestroyed(this)
      )
      .subscribe((option) => select.patchValue(option, { emitEvent: false }));

    (select.valueChanges as Observable<PermissionSelectOption>)
      .pipe(withLatestFrom(this.user$), untilDestroyed(this))
      .subscribe(([option, user]) =>
        this.projectMembersService.setProjectMemberPermissions(
          user,
          option.level
        )
      );
  }

  @Input() set user(user: string) {
    this.user$.next(user);
  }
}
