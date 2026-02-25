import { Inject, Injectable } from '@angular/core';
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import {
  AppSearchResult,
  AtlasEntitySearchObject,
} from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { zip } from 'lodash';
import { AtlasTypeIconDefinitionClass, iconsByType } from '../../meta';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider,
} from '../../services/element-search/app-search-document-provider';

export interface Breadcrumb {
  readonly class: AtlasTypeIconDefinitionClass;
  readonly guid: string;
  readonly icon: IconDefinition;
  readonly name: string;
  readonly typeName: string;
}

function fmtBreadcrumb([guid, name, typeName]: [
  string,
  string,
  string
]): Breadcrumb {
  return {
    guid,
    name,
    typeName,
    class: iconsByType[typeName]?.classIcon,
    icon: iconsByType[typeName]?.icon,
  };
}

export interface BreadCrumbsStoreContext {
  readonly breadcrumbs?: Breadcrumb[];
  readonly breadcrumbWarning?: string;
}

@Injectable()
export class BreadCrumbsService extends BasicStore<BreadCrumbsStoreContext> {
  constructor(
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AtlasEntitySearchObject>
  ) {
    super();
    this.init();
  }

  private init() {
    this.searchResultService.document$
      .pipe(untilDestroyed(this))
      .subscribe((searchResult) => this.handleUpdateBreadcrumbs(searchResult));
  }

  private handleUpdateBreadcrumbs(
    searchResult: AppSearchResult<AtlasEntitySearchObject>
  ) {
    // Preserve breadcrumbs when the document hasn't loaded yet
    if (searchResult == null) return;

    const guids = searchResult?.breadcrumbguid?.raw ?? [],
      names = searchResult?.breadcrumbname?.raw ?? [],
      typeNames = searchResult?.breadcrumbtype?.raw ?? [];

    // Clear breadcrumbs and show warning when data is mismatched (indicates partial/corrupt data)
    if (guids.length !== names.length || names.length !== typeNames.length) {
      this.update({
        description: 'Breadcrumb data is incomplete',
        payload: { breadcrumbs: [], breadcrumbWarning: 'Breadcrumb path could not be determined' },
      });
      return;
    }

    this.update({
      description: 'New breadcrumbs available',
      payload: { breadcrumbs: zip(guids, names, typeNames).map(fmtBreadcrumb), breadcrumbWarning: undefined },
    });
  }
}
