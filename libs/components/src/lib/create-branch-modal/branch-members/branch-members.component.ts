import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { faTimes, faUser, faUsers } from '@fortawesome/free-solid-svg-icons';
import { BranchPermissionLevel } from '@models4insight/repository';
import { Dictionary, identity, orderBy } from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { map, shareReplay, startWith } from 'rxjs/operators';
import {
  FuzzySearchInputComponent,
  FuzzySearchTokenizerConfig,
} from '../../fuzzy-search-input';
import { SortableTableShellConfig } from '../../sortable-table-shell';
import { CreateBranchModalService } from '../create-branch-modal.service';

const membersTableConfig: SortableTableShellConfig = {
  member_icon: { isNarrow: true, isStatic: true },
  member_name: {
    displayName: 'Username',
    description: 'The name of the member',
    isStatic: true,
  },
  permission: {
    displayName: 'Access rights',
    description:
      'Defines the level of access this user has to models in this branch',
    isStatic: true,
  },
  remove_member: {
    isNarrow: true,
    isStatic: true,
  },
};

export interface NameSearchEntity {
  readonly name: string;
}

const nameSearchTokenizerConfig: FuzzySearchTokenizerConfig<NameSearchEntity> =
  {
    name: {},
  };

@Component({
  selector: 'models4insight-branch-members',
  templateUrl: 'branch-members.component.html',
  styleUrls: ['branch-members.component.scss'],
})
export class BranchMembersComponent implements OnInit {
  readonly faTimes = faTimes;
  readonly faUser = faUser;
  readonly faUsers = faUsers;

  readonly nameSearchTokenizerConfig = nameSearchTokenizerConfig;
  readonly membersTableConfig = membersTableConfig;

  @Output() readonly removed: EventEmitter<string> = new EventEmitter<string>();

  @ViewChild(FuzzySearchInputComponent, { static: true })
  private readonly filter: FuzzySearchInputComponent<NameSearchEntity>;

  @Input() members: UntypedFormGroup;

  filteredMembers$: Observable<string[]>;
  memberNames$: Observable<NameSearchEntity[]>;
  nameTypeIndex$: Observable<Dictionary<'user' | 'group'>>;
  query$: Observable<string>;

  constructor(
    private readonly createBranchModalService: CreateBranchModalService
  ) {}

  ngOnInit() {
    this.memberNames$ = this.members.valueChanges.pipe(
      startWith(this.members.value),
      map(Object.keys),
      map((names) => names.map((name) => ({ name }))),
      shareReplay()
    );

    this.query$ = this.filter.queryChanged.pipe(startWith(''), shareReplay());

    this.filteredMembers$ = combineLatest([
      this.memberNames$.pipe(map((names) => names.map(({ name }) => name))),
      this.filter.suggestionsChanged.pipe(
        startWith([] as NameSearchEntity[]),
        map((names) => names.map(({ name }) => name))
      ),
      this.query$,
    ]).pipe(
      map(([members, filteredMembers, query]) =>
        // Filtered members are previously sorted by relevance to the current search query
        // When passing the full members array, sort alphabetically
        query ? filteredMembers : orderBy(members, identity, 'asc')
      )
    );

    this.nameTypeIndex$ = this.createBranchModalService.select('nameTypeIndex');
  }

  removeMember(event: boolean, username: string) {
    if (event) {
      this.removed.emit(username);
    }
  }

  trackByUsername(index: number, username: string) {
    return username;
  }

  updateUserPermission(
    username: string,
    permissionLevel: BranchPermissionLevel
  ) {
    this.members.patchValue({ [username]: permissionLevel });
  }
}
