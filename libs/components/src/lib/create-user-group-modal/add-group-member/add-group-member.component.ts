import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { UntypedFormArray } from '@angular/forms';
import { faPlus, faUser, faUsers } from '@fortawesome/free-solid-svg-icons';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { map, shareReplay, startWith } from 'rxjs/operators';
import {
  FuzzySearchInputComponent,
  FuzzySearchTokenizerConfig,
} from '../../fuzzy-search-input';
import { SortableTableShellConfig } from '../../sortable-table-shell';
import { CreateUserGroupModalService } from '../create-user-group-modal.service';

const suggestionsTableConfig: SortableTableShellConfig = {
  member_icon: { isNarrow: true, isStatic: true },
  suggestion: {
    displayName: 'Username',
    description: 'The name of the suggested member',
    isStatic: true,
  },
  add_member: { isStatic: true },
};

export interface NameSearchEntity {
  readonly name: string;
}

const nameSearchTokenizerConfig: FuzzySearchTokenizerConfig<NameSearchEntity> =
  {
    name: {},
  };

@Component({
  selector: 'models4insight-add-group-member',
  templateUrl: 'add-group-member.component.html',
  styleUrls: ['add-group-member.component.scss'],
})
export class AddGroupMemberComponent implements OnInit {
  readonly faPlus = faPlus;
  readonly faUser = faUser;
  readonly faUsers = faUsers;

  readonly nameSearchTokenizerConfig = nameSearchTokenizerConfig;
  readonly suggestionsTableConfig = suggestionsTableConfig;

  @Output() readonly added: EventEmitter<string> = new EventEmitter<string>();

  @Input() members: UntypedFormArray;

  connectedGroups$: Observable<string[]>;
  filterTerms$: Observable<string[]>;
  nameTypeIndex$: Observable<Dictionary<'user' | 'group'>>;
  suggestions$: Observable<string[]>;
  searchTerms$: Observable<NameSearchEntity[]>;

  @ViewChild(FuzzySearchInputComponent, { static: true })
  private readonly search: FuzzySearchInputComponent<NameSearchEntity>;

  constructor(
    private readonly createUserGroupModalService: CreateUserGroupModalService
  ) {}

  ngOnInit() {
    this.connectedGroups$ =
      this.createUserGroupModalService.select('connectedGroups');

    this.filterTerms$ = this.createUserGroupModalService
      .select('currentGroupName')
      .pipe(map((groupName) => [groupName]));

    this.nameTypeIndex$ = this.createUserGroupModalService
      .select('nameTypeIndex')
      .pipe(shareReplay());

    this.searchTerms$ = this.nameTypeIndex$.pipe(
      map(Object.keys),
      map((names) => names.map((name) => ({ name })))
    );

    this.suggestions$ = this.search.suggestionsChanged.pipe(
      startWith([] as NameSearchEntity[]),
      // Take only the top 3 suggestions
      map((suggestions) => suggestions.slice(0, 3)),
      map((suggestions) => suggestions.map(({ name }) => name))
    );
  }

  addMember(username: string) {
    this.added.emit(username);
  }
}
