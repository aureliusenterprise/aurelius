import { Component, Inject, Input, Optional } from '@angular/core';
import { AppSearchDocument } from '@models4insight/atlas/api';
import { combineLatest, map, Observable, of, switchMap } from 'rxjs';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider,
} from '../../services/element-search/app-search-document-provider';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

@Component({
  selector: 'models4insight-description',
  templateUrl: './description.component.html',
  styleUrls: ['./description.component.scss'],
})
export class DescriptionComponent {
  description$: Observable<string>;

  @Input() showPlaceholder = true;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    @Optional()
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AppSearchDocument>
  ) {
    const atlasDescription$ = this.entityDetailsService
      .select(['entityDetails', 'entity', 'typeName'], { includeFalsy: true })
      .pipe(switchMap((typeName) => this.selectDescriptionField(typeName)));

    const searchDescription$: Observable<string> = this.searchResultService
      ? this.searchResultService.document$.pipe(
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          map((doc) => (doc as any)?.definition?.raw ?? null)
        )
      : of(null);

    this.description$ = combineLatest([atlasDescription$, searchDescription$]).pipe(
      map(([atlasDescription, searchDescription]) => atlasDescription || searchDescription)
    );
  }

  private selectDescriptionField(typeName: string): Observable<string> {
    if (typeName === 'm4i_gov_data_quality' || typeName === 'm4i_data_quality') {
      return this.entityDetailsService.select(
        ['entityDetails', 'entity', 'attributes', 'ruleDescription'],
        { includeFalsy: true }
      );
    } else {
      return this.entityDetailsService.select(
        ['entityDetails', 'entity', 'attributes', 'definition'],
        { includeFalsy: true }
      );
    }
  }
}
