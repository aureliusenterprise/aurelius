import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { faPlus, faUser, faUsers } from '@fortawesome/free-solid-svg-icons';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { map, shareReplay, startWith } from 'rxjs/operators';
import {
  FuzzySearchInputComponent,
  FuzzySearchTokenizerConfig,
} from '../../fuzzy-search-input';
import { SortableTableShellConfig } from '../../sortable-table-shell';
import { CreateBranchModalService } from '../create-branch-modal.service';

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
  selector: 'models4insight-add-branch-member',
  templateUrl: 'add-branch-member.component.html',
  styleUrls: ['add-branch-member.component.scss'],
})
export class AddBranchMemberComponent implements OnInit {
  readonly faPlus = faPlus;
  readonly faUser = faUser;
  readonly faUsers = faUsers;

  readonly nameSearchTokenizerConfig = nameSearchTokenizerConfig;
  readonly suggestionsTableConfig = suggestionsTableConfig;

  @ViewChild(FuzzySearchInputComponent, { static: true })
  private readonly search: FuzzySearchInputComponent<NameSearchEntity>;

  @Input() members: UntypedFormGroup;

  @Output() added: EventEmitter<string> = new EventEmitter<string>();

  nameTypeIndex$: Observable<Dictionary<'user' | 'group'>>;
  searchTerms$: Observable<NameSearchEntity[]>;
  suggestions$: Observable<string[]>;

  constructor(
    private readonly createBranchModalService: CreateBranchModalService
  ) {}

  ngOnInit() {
    this.nameTypeIndex$ = this.createBranchModalService
      .select('nameTypeIndex')
      .pipe(shareReplay());

    this.searchTerms$ = this.nameTypeIndex$.pipe(
      map(Object.keys),
      map((names) => names.map((name) => ({ name })))
    );

    this.suggestions$ = this.search.suggestionsChanged.pipe(
      startWith([] as NameSearchEntity[]),
      // Only display the top 3 suggestions
      map((suggestions) => suggestions.slice(0, 3)),
      map((suggestions) => suggestions.map(({ name }) => name))
    );
  }

  addMember(username: string) {
    this.added.emit(username);
  }

  trackByUsername(index: number, username: string) {
    return username;
  }
}
