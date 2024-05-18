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

  set breadcrumbs(breadcrumbs: Breadcrumb[]) {
    this.update({
      description: 'New breadcrumbs available',
      payload: { breadcrumbs },
    });
  }

  private handleUpdateBreadcrumbs(
    searchResult: AppSearchResult<AtlasEntitySearchObject>
  ) {
    const guids = searchResult?.breadcrumbguid?.raw ?? [],
      names = searchResult?.breadcrumbname?.raw ?? [],
      typeNames = searchResult?.breadcrumbtype?.raw ?? [];

    // If the lengths of the arrays do not match, assume no breadcrumb is available.
    if (!(guids.length === names.length && names.length === typeNames.length)) {
      this.breadcrumbs = [];
      return;
    }

    this.breadcrumbs = zip(guids, names, typeNames).map(fmtBreadcrumb);
  }
}
