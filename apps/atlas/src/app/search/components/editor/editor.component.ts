import { Component, OnDestroy, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import {
  EntityAuditEvent,
  GovQualityApi,
  GovQualityApiClient
} from '@models4insight/atlas/api';
import { DynamicComponentDirective } from '@models4insight/directives';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EntityAuditService } from '../../services/entity-audit/entity-audit.service';
import { EntityDeleteService } from '../../services/entity-delete/entity-delete.service';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { EntityUpdateService } from '../../services/entity-update/entity-update.service';
import { Editor, editorsByType } from './editors-by-type';
import { EditorGovQualitySearchService } from './services/editor-gov-quality-search.service';

@Component({
  selector: 'models4insight-editor',
  templateUrl: 'editor.component.html',
  styleUrls: ['editor.component.scss'],
  providers: [
    EntityAuditService,
    EntityDeleteService,
    EntityUpdateService,
    EditorGovQualitySearchService,
    GovQualityApiClient,
    GovQualityApi,
  ],
})
export class EditorComponent implements OnDestroy {
  audits$: Observable<EntityAuditEvent[]>;
  deleteAllowed$: Observable<boolean>;
  editorComponent$: Observable<Editor>;
  editTypeAllowed$: Observable<boolean>;
  isDeletingEntity$: Observable<boolean>;
  isUpdatingEntity$: Observable<boolean>;

  currentTab: 'entity' | 'history' = 'entity';

  @ViewChild(DynamicComponentDirective, { static: false })
  private readonly editorComponent: DynamicComponentDirective<Editor>;

  constructor(
    private readonly entityAuditService: EntityAuditService,
    private readonly entityDeleteService: EntityDeleteService,
    private readonly entityDetailsService: EntityDetailsService,
    private readonly entityUpdateService: EntityUpdateService,
    private readonly router: Router
  ) {
    this.audits$ = this.entityAuditService.select('audits');

    this.editorComponent$ = this.entityDetailsService.entityDetails$.pipe(
      map((entity) => editorsByType[entity.typeName])
    );

    this.deleteAllowed$ = this.entityDetailsService
      .select(['entityDetails', 'entity', 'guid'])
      .pipe(map((guid) => !guid.startsWith('-')));

    this.editTypeAllowed$ = this.entityDetailsService
      .select(['entityDetails', 'entity', 'guid'])
      .pipe(map((guid) => guid.startsWith('-')));

    this.isDeletingEntity$ =
      this.entityDeleteService.select('isDeletingEntity');

    this.isUpdatingEntity$ =
      this.entityUpdateService.select('isUpdatingEntity');

    this.entityDeleteService.entityDeleted
      .pipe(untilDestroyed(this))
      .subscribe(() => this.onEntityDeleted());

    this.entityUpdateService.entityUpdated
      .pipe(untilDestroyed(this))
      .subscribe((guid) => this.onEntityUpdated(guid));
  }

  ngOnDestroy() {}

  activate() {
    const editorComponent = this.editorComponent?.instance;
    editorComponent?.editorFormService.update();
  }

  deleteEntity(confirmed: boolean) {
    if (!confirmed) return;

    this.entityDeleteService.deleteEntity();
  }

  onEntityDeleted() {
    this.router.navigate(['search']);
  }

  onEntityUpdated(guid: string) {
    this.router.navigate(['search', 'details', guid]);
  }

  saveEntity() {
    const editorComponent = this.editorComponent?.instance;
    editorComponent?.editorFormService.submit();
  }
}
