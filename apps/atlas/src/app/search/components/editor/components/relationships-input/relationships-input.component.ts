import {
  Component,
  ElementRef,
  Input,
  OnDestroy,
  OnInit,
  ViewChild
} from '@angular/core';
import { FormArray, FormControl } from '@angular/forms';
import {
  AppSearchResult,
  AssignedEntity,
  AtlasEntitySearchObject,
  ElasticSearchResult,
  EntityValidationResult
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { startWith } from 'rxjs/operators';
import { iconsByType } from '../../../../meta';
import { AppSearchResultsService } from '../../../../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../../../../services/app-search-results/entity-search-results.service';
import { FilterService } from '../../../../services/filter/filter.service';
import { EntitySearchObject } from '../../../../services/search/entity-search.service';
import { SearchService } from '../../../../services/search/search.service';
import { generatePlaceholderId } from '../../../../utils';
import { RelationshipsInputSearchService } from './relationships-input-search.service';
import { RelationshipsInputService } from './relationships-input.service';

@Component({
  selector: 'models4insight-relationships-input',
  templateUrl: 'relationships-input.component.html',
  styleUrls: ['relationships-input.component.scss'],
  providers: [
    FilterService,
    RelationshipsInputService,
    { provide: SearchService, useClass: RelationshipsInputSearchService },
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
  ],
})
export class RelationshipsInputComponent implements OnInit, OnDestroy {
  readonly iconsByType = iconsByType;
  readonly input = new FormControl<string>('');

  readonly options$: Observable<AppSearchResult<EntitySearchObject>[]>;

  hasFocus = false;

  @Input() relationshipTypeName: string;
  @Input() tags: FormArray<FormControl<AssignedEntity>>;
  @Input() rule: EntityValidationResult;

  @ViewChild('inputElement', { static: true })
  private readonly inputElement: ElementRef<HTMLInputElement>;

  constructor(
    private readonly relationshipsInputService: RelationshipsInputService,
    private readonly searchResultsService: AppSearchResultsService<EntitySearchObject>,
    private readonly searchService: SearchService<
      AtlasEntitySearchObject,
      EntitySearchObject
    >
  ) {
    this.options$ = this.searchResultsService.results$;
  }

  ngOnInit() {
    this.input.valueChanges
      .pipe(startWith(this.input.value), untilDestroyed(this))
      .subscribe((query) => (this.searchService.query = query));

    this.tags.valueChanges
      .pipe(startWith(this.tags.value), untilDestroyed(this))
      .subscribe(
        (relationships) =>
          (this.relationshipsInputService.relationships = relationships.map(
            (relationship) => relationship.guid
          ))
      );
  }

  ngOnDestroy() {}

  addTag(searchResult: ElasticSearchResult) {
    const relationship: AssignedEntity = {
      guid: searchResult.guid.raw,
      typeName: searchResult.typename?.raw,
      displayText: searchResult.name?.raw,
      entityStatus: 'ACTIVE',
      relationshipGuid: generatePlaceholderId(),
      relationshipType: this.relationshipTypeName,
      relationshipStatus: 'ACTIVE',
      relationshipAttributes: {
        typeName: this.relationshipTypeName,
      },
    };

    this.tags.push(new FormControl(relationship));
    this.input.reset('');
  }

  deleteTag(index: number) {
    this.tags.removeAt(index);
  }

  focusInput() {
    this.inputElement.nativeElement.focus();
  }

  preventBlur(event: Event) {
    event.preventDefault();
  }

  trackByGuid(_: number, searchResult: AppSearchResult<EntitySearchObject>) {
    return searchResult.guid?.raw;
  }

  @Input() set typeName(typeName: string) {
    this.relationshipsInputService.typeName = typeName;
  }
}
