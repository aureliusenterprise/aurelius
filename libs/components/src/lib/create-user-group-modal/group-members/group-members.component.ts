import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { UntypedFormArray } from '@angular/forms';
import { faTimes, faUser, faUsers } from '@fortawesome/free-solid-svg-icons';
import { Dictionary, identity, orderBy } from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { map, shareReplay, startWith } from 'rxjs/operators';
import {
  FuzzySearchInputComponent,
  FuzzySearchTokenizerConfig,
} from '../../fuzzy-search-input';
import { SortableTableShellConfig } from '../../sortable-table-shell';
import { CreateUserGroupModalService } from '../create-user-group-modal.service';

const membersTableConfig: SortableTableShellConfig = {
  member_icon: { isNarrow: true, isStatic: true },
  member_name: {
    displayName: 'Username',
    description: 'The name of the member',
    isStatic: true,
  },
  add_member: { isNarrow: true, isStatic: true },
};

export interface NameSearchEntity {
  readonly name: string;
}

const nameSearchTokenizerConfig: FuzzySearchTokenizerConfig<NameSearchEntity> =
  {
    name: {},
  };

@Component({
  selector: 'models4insight-group-members',
  templateUrl: 'group-members.component.html',
  styleUrls: ['group-members.component.scss'],
})
export class GroupMembersComponent implements OnInit {
  readonly faTimes = faTimes;
  readonly faUser = faUser;
  readonly faUsers = faUsers;

  readonly membersTableConfig = membersTableConfig;
  readonly nameSearchTokenizerConfig = nameSearchTokenizerConfig;

  @Input() members: UntypedFormArray;

  filteredMemberNames$: Observable<string[]>;
  memberNames$: Observable<NameSearchEntity[]>;
  nameTypeIndex$: Observable<Dictionary<'user' | 'group'>>;
  query$: Observable<string>;

  @ViewChild(FuzzySearchInputComponent, { static: true })
  private readonly filter: FuzzySearchInputComponent<NameSearchEntity>;

  constructor(
    private readonly createUserGroupModalService: CreateUserGroupModalService
  ) {}

  ngOnInit() {
    this.memberNames$ = this.members.valueChanges.pipe(
      startWith(this.members.value),
      map((members = []) => members.map((member) => ({ name: member }))),
      shareReplay()
    );

    this.query$ = this.filter.queryChanged.pipe(startWith(''), shareReplay());

    this.filteredMemberNames$ = combineLatest([
      this.memberNames$.pipe(map((names) => names.map(({ name }) => name))),
      this.filter.suggestionsChanged.pipe(
        startWith([] as NameSearchEntity[]),
        map((suggestions) => suggestions.map((suggestion) => suggestion.name))
      ),
      this.query$,
    ]).pipe(
      map(([members, filteredMembers, query]) =>
        // Filtered members are previously sorted by relevance to the current search query
        // When passing the full members array, sort alphabetically
        query ? filteredMembers : orderBy(members, identity, 'asc')
      )
    );

    this.nameTypeIndex$ =
      this.createUserGroupModalService.select('nameTypeIndex');
  }

  removeMember(event: boolean, username: string) {
    if (event) {
      this.members.removeAt(
        this.members.controls.findIndex((control) => control.value === username)
      );
    }
  }

  trackByUsername(index: number, username: string) {
    return username;
  }
}
