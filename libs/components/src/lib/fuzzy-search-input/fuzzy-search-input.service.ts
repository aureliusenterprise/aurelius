import { OnDestroy, Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import {
  iterate,
  substrings,
  SubType,
  untilDestroyed,
} from '@models4insight/utils';
import { product } from 'cartesian-product-generator';
import { deburr, identity, lowerCase, orderBy } from 'lodash';
import InvertedIndex from 'mnemonist/inverted-index';
import { add } from 'mnemonist/set';
import SymSpell, { SymSpellOptions } from 'mnemonist/symspell';
import { combineLatest } from 'rxjs';
import { map, shareReplay, switchMap } from 'rxjs/operators';

const SPLIT_PATTERN = /[^a-z0-9]+/gim;

export interface FuzzySearchTokenizerConfigEntry {
  /**
   * Whether or not only the complete value should be matched.
   */
  readonly static?: boolean;
}

export type FuzzySearchTokenizerConfig<T> = {
  [propertyName in keyof SubType<T, string>]?: FuzzySearchTokenizerConfigEntry;
};

export const stringTokenizer: FuzzySearchTokenizerFunction<string> = (
  item: string
) => {
  if (typeof item !== 'string') return [];
  const trimmed = item.trim();
  const result = new Set<string>();
  for (const token of deburr(lowerCase(trimmed)).split(SPLIT_PATTERN)) {
    result.add(token);
  }
  return Array.from(result);
};

const MIN_TOKEN_LENGTH = 2;

function* resolveSearchQueryTokens(
  query: string,
  containsSearchIndex: InvertedIndex<string>,
  fuzzySearchIndex: SymSpell
) {
  const queryTokens = stringTokenizer(query);
  const seenTokens = new Set<string>();

  for (const token of queryTokens) {
    if (token.length < MIN_TOKEN_LENGTH || seenTokens.has(token)) continue;

    // Try to match the given string to a known entry in the search index.
    // Order the matches found from shortest to longest to have the closest matches first.
    let searchTokens = orderBy(
      containsSearchIndex.get(token) ?? [],
      'length',
      'asc'
    );

    // If no matching entries are found, try to correct the spelling to a known entry.
    // The returned matches are already ordered best to worst by the algorithm.
    if (searchTokens.length === 0) {
      searchTokens = fuzzySearchIndex.search(token).map(({ term }) => term);
    }

    // Reduce query complexity by filtering out tokens we've already seen
    const result = searchTokens.filter(
      (searchToken) => !seenTokens.has(searchToken)
    );

    // If any new tokens were found, return the tokens and add them to the tokens seen
    if (result.length > 0) {
      yield result;
      add(seenTokens, new Set(result));
    }

    seenTokens.add(token);
  }
}

export type FuzzySearchTokenizerFunction<T> = (item: T) => string[];

export interface FuzzySearchInputStoreContext<T> {
  readonly containsSearchIndex?: InvertedIndex<string>;
  readonly exactSearchIndex?: InvertedIndex<T>;
  readonly fuzzySearchIndex?: SymSpell;
  readonly isCreatingContainsSearchIndex?: boolean;
  readonly isCreatingFuzzySearchIndex?: boolean;
  readonly isCreatingSearchIndex?: boolean;
  readonly isUpdatingSuggestions?: boolean;
  readonly query?: string;
  readonly searchItems?: T[];
  readonly suggestions?: T[];
  readonly tokenizedSearchIndex?: InvertedIndex<T>;
  readonly tokenizerConfig?: FuzzySearchTokenizerConfig<T>;
}

export const defaultFuzzySeachInputServiceState = {
  filterTerms: [],
  isCreatingSubstringMap: false,
  isCreatingWordCloud: false,
  isCreatingSearchIndex: false,
  isUpdatingSuggestions: false,
};

const symSpellOptions: SymSpellOptions = {
  maxDistance: 2, // Builds a search index with a maximum edit distance of 2
  verbosity: 2, // Returns all suggestions within the max edit distance
};

// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
@Injectable()
export class FuzzySearchInputService<T>
  extends BasicStore<FuzzySearchInputStoreContext<T>>
  implements OnDestroy
{
  constructor() {
    super({ defaultState: defaultFuzzySeachInputServiceState });
    this.init();
  }

  ngOnDestroy() {}

  private init() {
    combineLatest([this.select('searchItems'), this.select('tokenizerConfig')])
      .pipe(
        switchMap(([searchItems, tokenizerConfig]) =>
          this.handleCreateSearchIndex(searchItems, tokenizerConfig)
        ),
        untilDestroyed(this)
      )
      .subscribe();

    const searchTerms = this.select('tokenizedSearchIndex').pipe(
      map((index) => Array.from(iterate(index.tokens()))),
      shareReplay()
    );

    // Whenever the search terms update, create a new search index for the contains search
    searchTerms
      .pipe(
        switchMap((terms) => this.handleCreateContainsSearchIndex(terms)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the search terms update, create a new search index for the fuzzy search
    searchTerms
      .pipe(
        switchMap((terms) => this.handleCreateFuzzySearchIndex(terms)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the filter terms or the query update, update the suggestions
    this.select('query')
      .pipe(
        switchMap((query) => this.handleUpdateSuggestions(query)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  @ManagedTask('Creating the search index', { isQuiet: true })
  @MonitorAsync('isCreatingSearchIndex')
  private async handleCreateSearchIndex(
    items: T[],
    tokenizerConfig: FuzzySearchTokenizerConfig<T>
  ) {
    const exactSearchTokenizer = (item: T) => {
      if (item === null || item === undefined) return [];
      const tokens = new Set<string>();
      for (const [propertyName, config] of Object.entries(tokenizerConfig)) {
        if ((config as FuzzySearchTokenizerConfigEntry).static) {
          const value = item[propertyName] as string;
          if (value) {
            tokens.add(deburr(value.trim().toLowerCase()));
          }
        }
      }
      return Array.from(tokens);
    };

    const exactSearchIndex = InvertedIndex.from(items, [
      exactSearchTokenizer,
      identity,
    ]);

    const tokenizedSearchTokenizer = (item: T) => {
      if (item === null || item === undefined) return [];
      const tokens = new Set<string>();
      for (const [propertyName, config] of Object.entries(tokenizerConfig)) {
        if (!(config as FuzzySearchTokenizerConfigEntry).static) {
          for (const token of stringTokenizer(item[propertyName])) {
            tokens.add(token);
          }
        }
      }
      return Array.from(tokens);
    };

    const tokenizedSearchIndex = InvertedIndex.from(items, [
      tokenizedSearchTokenizer,
      identity,
    ]);

    this.update({
      description: 'New search index available',
      payload: { exactSearchIndex, tokenizedSearchIndex },
    });
  }

  @ManagedTask('Creating the contains search index', { isQuiet: true })
  @MonitorAsync('isCreatingContainsSearchIndex')
  private async handleCreateContainsSearchIndex(searchTokens: string[]) {
    const containsSearchItemTokenizer = (item: string) => {
      if (typeof item !== 'string') return [];
      if (item.startsWith('id_')) return [item];
      return Array.from(substrings(item, { minLength: MIN_TOKEN_LENGTH }));
    };

    const containsSearchIndex = InvertedIndex.from(searchTokens, [
      containsSearchItemTokenizer,
      (query) => [query],
    ]);

    this.update({
      description: 'New search index available',
      payload: { containsSearchIndex },
    });
  }

  @ManagedTask('Creating the fuzzy search index', { isQuiet: true })
  @MonitorAsync('isCreatingFuzzySearchIndex')
  private async handleCreateFuzzySearchIndex(searchTokens: string[]) {
    const filteredSearchTokens = searchTokens.filter(
      (token) => typeof token === 'string' && !token.startsWith('id_')
    );

    const fuzzySearchIndex = SymSpell.from(
      filteredSearchTokens,
      symSpellOptions
    );

    this.update({
      description: 'New search index available',
      payload: {
        fuzzySearchIndex,
      },
    });
  }

  @ManagedTask('Updating the search suggestions', { isQuiet: true })
  @MonitorAsync('isUpdatingSuggestions')
  private async handleUpdateSuggestions(query: string) {
    let suggestions: T[] = [];

    if (query) {
      const [
        exactSearchIndex,
        tokenizedSearchIndex,
        containsSearchIndex,
        fuzzySearchIndex,
      ] = await Promise.all([
        this.get('exactSearchIndex'),
        this.get('tokenizedSearchIndex'),
        this.get('containsSearchIndex'),
        this.get('fuzzySearchIndex'),
      ]);

      // First try to find any exact matches
      suggestions =
        exactSearchIndex.get([deburr(query.trim().toLowerCase())]) ?? [];

      // If no exact matches are found, continue with a tokenized search
      if (!suggestions.length) {
        const resolvedSearchQueryTokens = resolveSearchQueryTokens(
          query,
          containsSearchIndex,
          fuzzySearchIndex
        );

        const searchQueries = product(...resolvedSearchQueryTokens);

        for (const searchQuery of searchQueries) {
          const searchResult = tokenizedSearchIndex.get(searchQuery);
          if (searchResult) {
            suggestions = [...suggestions, ...searchResult];
          }
        }
      }
    }

    this.update({
      description: 'New search suggestions available',
      payload: {
        suggestions,
      },
    });
  }
}
