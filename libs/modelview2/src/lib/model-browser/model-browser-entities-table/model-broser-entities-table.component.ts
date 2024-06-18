import { Component, OnInit } from '@angular/core';
import {
  AbstractSortableTable,
  SortableTableShellConfig,
} from '@models4insight/components';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelEntity } from '../../parsers';

const entitiesTableConfig: SortableTableShellConfig<ModelEntity> = {
  type: {
    displayName: 'Type',
    description: 'The type of the entity',
    isNarrow: true,
  },
  name: { displayName: 'Name', description: 'The name of the entity' },
};

@Component({
  selector: 'models4insight-model-browser-entities-table',
  templateUrl: 'model-browser-entities-table.component.html',
  styleUrls: ['model-browser-entities-table.component.scss'],
})
export class ModelBrowserEntitiesTableComponent
  extends AbstractSortableTable<ModelEntity>
  implements OnInit
{
  readonly entitiesTableConfig = entitiesTableConfig;

  selectedEntity$: Observable<ModelEntity>;

  constructor(private readonly modelExplorerService: ModelExplorerService) {
    super();
  }

  ngOnInit() {
    this.selectedEntity$ = this.modelExplorerService
      .select('selectedEntity', { includeFalsy: true })
      .pipe(
        switchMap((id) =>
          this.modelExplorerService.select(['entitiesById', id], {
            includeFalsy: true,
          })
        )
      );
  }

  deselectEntity() {
    this.modelExplorerService.deleteConceptSelection();
  }

  selectEntity(entity: ModelEntity) {
    this.modelExplorerService.selectedEntity = entity.id;
  }
}
