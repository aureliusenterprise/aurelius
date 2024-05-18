import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { UntypedFormArray, UntypedFormControl } from '@angular/forms';
import { faHashtag } from '@fortawesome/free-solid-svg-icons';
import { Classification, ClassificationDef } from '@models4insight/atlas/api';
import { combineLatest, Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { EntityDetailsService } from '../../../../services/entity-details/entity-details.service';
import { TypeDefsService } from '../../../../services/type-defs/type-defs.service';

function filterClassifications(
  defs: ClassificationDef[],
  selected: Classification[],
  typeName: string,
  query?: string
) {
  const applicableDefs = defs.filter((def) =>
    def.entityTypes?.find((entityType) => entityType === typeName)
  );

  const defsNotSelected = applicableDefs.filter(
    (def) =>
      !selected.find((classification) => classification.typeName === def.name)
  );

  const defsMatchingQuery = query
    ? defsNotSelected.filter(
        (def) =>
          def.name?.toLowerCase().includes(query.toLowerCase()) ||
          def.description?.toLowerCase().includes(query.toLowerCase())
      )
    : defsNotSelected;

  return defsMatchingQuery;
}

@Component({
  selector: 'models4insight-classifications-input',
  templateUrl: 'classifications-input.component.html',
  styleUrls: ['classifications-input.component.scss'],
})
export class ClassificationsInputComponent implements OnInit {
  readonly input = new UntypedFormControl(null);
  readonly faHashtag = faHashtag;

  options$: Observable<ClassificationDef[]>;

  hasFocus = false;
  @Input() tags: UntypedFormArray;

  @ViewChild('inputElement', { static: true })
  private readonly inputElement: ElementRef<HTMLInputElement>;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly typeDefsService: TypeDefsService
  ) {}

  ngOnInit() {
    const typeName$ = this.entityDetailsService.entityDetails$.pipe(
      map((entity) => entity.typeName)
    );

    this.options$ = combineLatest([
      this.typeDefsService.select(['typeDefs', 'classificationDefs']),
      this.tags.valueChanges.pipe(startWith(this.tags.value)),
      typeName$,
      this.input.valueChanges.pipe(startWith(this.input.value)),
    ]).pipe(
      map(([defs, selected, typeName, query]) =>
        filterClassifications(defs, selected, typeName, query)
      )
    );
  }

  async addTag(typeName: string) {
    const entityId = await this.entityDetailsService.get([
      'entityDetails',
      'entity',
      'guid',
    ]);

    this.tags.push(
      new UntypedFormControl({
        entityGuid: entityId,
        entityStatus: 'ACTIVE',
        propagate: true,
        removePropagationsOnEntityDelete: true,
        typeName,
      })
    );
    this.input.reset();
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
}
