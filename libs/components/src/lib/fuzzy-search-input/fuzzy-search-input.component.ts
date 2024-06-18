import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { UntypedFormControl } from '@angular/forms';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import {
  AbstractControlShell,
  ControlShellContext,
  defaultControlShellContext,
} from '../control-shell';
import {
  FuzzySearchInputService,
  FuzzySearchTokenizerConfig,
} from './fuzzy-search-input.service';

const defaultFuzzySearchInputContext: ControlShellContext = {
  ...defaultControlShellContext,
  icon: faSearch,
};

@Component({
  selector: 'models4insight-fuzzy-search-input',
  templateUrl: 'fuzzy-search-input.component.html',
  styleUrls: ['fuzzy-search-input.component.scss'],
  providers: [FuzzySearchInputService],
})
export class FuzzySearchInputComponent<T = string>
  extends AbstractControlShell
  implements OnInit, OnDestroy
{
  /**
   * Emits whenever the suggestions start and stop updating
   */
  @Output() readonly isUpdatingSuggestions = new EventEmitter<boolean>();

  /**
   * Emits whenever the search query updates
   */
  @Output() readonly queryChanged = new EventEmitter<string>();

  /**
   * Emits whenever a new set of suggestions becomes available
   */
  @Output() readonly suggestionsChanged = new EventEmitter<T[]>();

  isUpdatingSearchIndex$: Observable<boolean>;
  isUpdatingSuggestions$: Observable<boolean>;

  constructor(private readonly searchService: FuzzySearchInputService<T>) {
    super();
  }

  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultFuzzySearchInputContext;
    }

    this.control = new UntypedFormControl(null);

    this.control.valueChanges
      .pipe(debounceTime(100), untilDestroyed(this))
      .subscribe((query) => (this.query = query));

    this.searchService
      .select('query')
      .pipe(untilDestroyed(this))
      .subscribe((query) =>
        this.control.patchValue(query, { emitEvent: false })
      );

    this.searchService
      .select('isUpdatingSuggestions')
      .pipe(untilDestroyed(this))
      .subscribe(this.isUpdatingSuggestions);

    this.searchService
      .select('query')
      .pipe(untilDestroyed(this))
      .subscribe(this.queryChanged);

    this.searchService
      .select('suggestions')
      .pipe(untilDestroyed(this))
      .subscribe(this.suggestionsChanged);

    this.isUpdatingSearchIndex$ = this.searchService.select(
      'isCreatingSearchIndex'
    );

    this.isUpdatingSuggestions$ = this.searchService.select(
      'isUpdatingSuggestions'
    );
  }

  ngOnDestroy() {}

  @Input() set query(query: string) {
    this.searchService.update({
      description: 'New search query available',
      payload: { query },
    });
  }

  @Input() set tokenizerConfig(tokenizerConfig: FuzzySearchTokenizerConfig<T>) {
    this.searchService.update({
      description: 'New tokenizer config available',
      payload: { tokenizerConfig },
    });
  }

  @Input() set searchItems(searchItems: T[]) {
    this.searchService.update({
      description: 'New search items available',
      payload: { searchItems },
    });
  }
}
