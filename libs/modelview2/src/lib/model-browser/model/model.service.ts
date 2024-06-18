import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelElement, ModelRelation, ModelEntity } from '../../parsers';

export interface ModelBrowserModelStoreContext {
  readonly suggestions?: ModelEntity[];
  readonly suggestedElements?: ModelElement[];
  readonly suggestedRelations?: ModelRelation[];
}

const defaultState: ModelBrowserModelStoreContext = { suggestions: [] };

@Injectable()
export class ModelBrowserModelService extends BasicStore<ModelBrowserModelStoreContext> {
  constructor(private readonly modelExplorerService: ModelExplorerService) {
    super({ defaultState });
    this.init();
  }

  private init() {
    this.select('suggestions')
      .pipe(
        switchMap((suggestions) => this.buildSearchResults(suggestions)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  get searchItems() {
    return combineLatest([
      this.modelExplorerService.select('elements'),
      this.modelExplorerService.select('relations'),
    ]).pipe(
      map(([elements, relations]) => [
        ...Object.values(elements),
        ...Object.values(relations),
      ])
    );
  }

  private async buildSearchResults(suggestions: ModelEntity[]) {
    const buildSearchResultsCategory = async <
      T extends 'elements' | 'relations'
    >(
      category: T
    ) => {
      const entities = await this.modelExplorerService.get(category);
      if (suggestions.length === 0) return Object.values(entities);

      const result = [];
      for (const suggestion of suggestions) {
        if (suggestion.id in entities) {
          result.push(suggestion);
        }
      }

      return result;
    };

    const [suggestedElements, suggestedRelations] = await Promise.all([
      buildSearchResultsCategory('elements'),
      buildSearchResultsCategory('relations'),
    ]);

    this.update({
      description: 'New search suggestions available',
      payload: {
        suggestedElements: suggestedElements as ModelElement[],
        suggestedRelations: suggestedRelations as ModelRelation[],
      },
    });
  }
}
