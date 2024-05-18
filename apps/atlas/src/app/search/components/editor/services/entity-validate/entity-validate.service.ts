import { Injectable } from '@angular/core';
import {
  AtlasEntityWithEXTInformation,
  EntityValidationResponse,
  GovQualityApi,
} from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { merge, Observable, of } from 'rxjs';
import { catchError, debounceTime, shareReplay, switchMap } from 'rxjs/operators';
import { EntityDetailsService } from '../../../../services/entity-details/entity-details.service';
import { EditorFormService } from '../editor-form.service';

export interface EntityValidateStoreContext {
  readonly isValidatingEntity?: boolean;
}

@Injectable()
export class EntityValidateService extends BasicStore<EntityValidateStoreContext> {
  readonly validationResults$: Observable<EntityValidationResponse>;

  constructor(
    private readonly editorFormService: EditorFormService,
    private readonly entityDetailsService: EntityDetailsService,
    private readonly govQualityApiService: GovQualityApi
  ) {
    super();

    this.validationResults$ = merge(
      this.entityDetailsService.select('entityDetails'),
      this.editorFormService.form.valueChanges.pipe(debounceTime(200))
    ).pipe(
      switchMap((entity) => this.validateEntity(entity)),
      shareReplay({ refCount: true })
    );
  }

  @ManagedTask('Validating the data governance quality', { isQuiet: true })
  @MonitorAsync('isValidatingEntity')
  private async validateEntity(entityFormData: AtlasEntityWithEXTInformation) {
    return this.govQualityApiService
      .validateEntity(entityFormData)
      .pipe(catchError(() => of({})))
      .toPromise();
  }
}
