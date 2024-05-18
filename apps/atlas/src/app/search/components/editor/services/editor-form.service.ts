import { Inject, Injectable, InjectionToken, OnDestroy } from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { AtlasEntityWithEXTInformation } from '@models4insight/atlas/api';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { cloneDeep } from 'lodash';
import { combineLatest, Subject, Subscription } from 'rxjs';
import { exhaustMap, startWith } from 'rxjs/operators';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { EntityUpdateService } from '../../../services/entity-update/entity-update.service';

export type EditorFormFactory = () => UntypedFormGroup;

export const EDITOR_FORM_FACTORY = new InjectionToken<EditorFormFactory>(
  'EDITOR_FORM_FACTORY'
);

export type EditorMergeStrategy = (
  entity: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) => AtlasEntityWithEXTInformation;

export const EDITOR_MERGE_STRATEGY = new InjectionToken<EditorMergeStrategy>(
  'EDITOR_MERGE_STRATEGY'
);

export type EditorUpdateStrategy = (
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) => void;

export const EDITOR_UPDATE_STRATEGY = new InjectionToken<EditorMergeStrategy>(
  'EDITOR_UPDATE_STRATEGY'
);

@Injectable()
export class EditorFormService implements OnDestroy {
  readonly form: UntypedFormGroup;

  private readonly submit$ = new Subject<void>();
  private readonly update$ = new Subject<void>();

  private formData$: Subscription;
  private submissions$: Subscription;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly entityUpdateService: EntityUpdateService,
    @Inject(EDITOR_FORM_FACTORY) readonly formFactory: EditorFormFactory,
    @Inject(EDITOR_MERGE_STRATEGY) readonly mergeStrategy: EditorMergeStrategy,
    @Inject(EDITOR_UPDATE_STRATEGY)
    readonly updateStrategy: EditorUpdateStrategy
  ) {
    this.form = formFactory();
    this.init();
  }

  private init() {
    this.formData$ = combineLatest([
      this.entityDetailsService.select('entityDetails'),
      this.update$.pipe(startWith(<string>undefined)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([entityDetails, _]) =>
        this.updateStrategy(entityDetails, this.form)
      );

    this.submissions$ = this.submit$
      .pipe(
        exhaustMap(() => this.handleSubmitForm()),
        untilDestroyed(this)
      )
      .subscribe();
  }

  ngOnDestroy() {
    this.formData$.unsubscribe();
    this.submissions$.unsubscribe();

    this.submit$.complete();
    this.update$.complete();
  }

  submit() {
    this.submit$.next();
  }

  update() {
    this.update$.next();
  }

  @ManagedTask('Submitting the form', { isQuiet: true })
  private async handleSubmitForm() {
    this.form.updateValueAndValidity();

    if (!this.form.valid) return;

    const entityDetails = await this.entityDetailsService.get('entityDetails');

    const updatedEntity = this.mergeStrategy(
      cloneDeep(entityDetails),
      this.form
    );

    this.entityUpdateService.updateEntity(updatedEntity);
  }
}
