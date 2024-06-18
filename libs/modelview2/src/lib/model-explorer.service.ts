import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ModelService } from '@models4insight/services/model';
import { ManagedTask } from '@models4insight/task-manager';
import {
  BidirectionalMultiMap,
  fromEntries,
  iterate,
  untilDestroyed,
} from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import {
  getParserForModel,
  ModelElement,
  ModelEntity,
  ModelInfo,
  ModelRelation,
  ModelView,
  ModelViewConnection,
  ModelViewNode,
} from './parsers';

export interface ModelExplorerStoreContext {
  readonly conceptsByRelationId?: Dictionary<string[]>;
  readonly elements?: Dictionary<ModelElement>;
  readonly entitiesById?: Dictionary<ModelEntity>;
  readonly entitiesByViewId?: Dictionary<string[]>;
  readonly highlightedEntity?: string;
  readonly info?: ModelInfo;
  readonly isBuildingConceptRelationMap?: boolean;
  readonly isBuildingEntityViewMap?: boolean;
  readonly isBuildingViewReferenceMap?: boolean;
  readonly isParsingModel?: boolean;
  readonly organizations?: Dictionary<string>;
  readonly relations?: Dictionary<ModelRelation>;
  readonly relationsByConceptId?: Dictionary<string[]>;
  readonly selectedEntity?: string;
  readonly views?: Dictionary<ModelView>;
  readonly viewsByEntityId?: Dictionary<string[]>;
}

@Injectable()
export class ModelExplorerService extends BasicStore<ModelExplorerStoreContext> {
  constructor(private readonly modelService: ModelService) {
    super();
    this.init();
  }

  private init() {
    combineLatest([
      this.select('elements'),
      this.select('relations'),
      this.select('views'),
    ])
      .pipe(
        switchMap(([elements, relations, views]) =>
          this.buildModelEntityIndex(elements, relations, views)
        ),
        untilDestroyed(this)
      )
      .subscribe();

    this.modelService
      .select('model')
      .pipe(
        switchMap((model) => this.handleParseModel(model)),
        untilDestroyed(this)
      )
      .subscribe();

    this.select('relations')
      .pipe(
        switchMap((relations) => this.buildConceptRelationMap(relations)),
        untilDestroyed(this)
      )
      .subscribe();

    this.select('views')
      .pipe(
        switchMap((views) => this.buildEntityViewMap(views)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  deleteConceptSelection() {
    this.delete({
      description: 'Concept entity cleared',
      path: ['selectedEntity'],
    });
  }

  set highlihghtedEntity(highlightedEntity: string) {
    this.update({
      description: `Highlighted entity ${highlightedEntity}`,
      payload: { highlightedEntity },
    });
  }

  set selectedEntity(selectedEntity: string) {
    this.update({
      description: `Selected entity ${selectedEntity}`,
      payload: { selectedEntity },
    });
  }

  @MonitorAsync('isParsingModel')
  @ManagedTask('Parsing the model', { isQuiet: true })
  private async handleParseModel(jsonModel: any) {
    const parser = getParserForModel(jsonModel);

    const parsedModel = await parser(jsonModel);

    this.update({
      description: 'New parsed model available',
      payload: parsedModel,
    });
  }

  @MonitorAsync('isBuildingConceptRelationMap')
  @ManagedTask('Mapping concepts and relations', { isQuiet: true })
  private async buildConceptRelationMap(relations: Dictionary<ModelRelation>) {
    const mapping = new BidirectionalMultiMap<string, string>();

    for (const [id, relation] of Object.entries(relations)) {
      mapping.set(id, relation.source);
      mapping.set(id, relation.target);
    }

    const conceptsByRelationId = fromEntries(
        iterate(mapping.mapping.associations())
      ),
      relationsByConceptId = fromEntries(
        iterate(mapping.inverse.associations())
      );

    this.update({
      description: 'New view reference mapping available',
      payload: {
        conceptsByRelationId: conceptsByRelationId as Dictionary<string[]>,
        relationsByConceptId: relationsByConceptId as Dictionary<string[]>,
      },
    });
  }

  @MonitorAsync('isBuildingEntityViewMap')
  @ManagedTask('Mapping entities and views', { isQuiet: true })
  private async buildEntityViewMap(views: Dictionary<ModelView>) {
    function* findReferencedConcepts(view: ModelView) {
      const nodes = Object.values(view.nodes);
      for (const { ref, id } of nodes) {
        yield id;
        if (ref) {
          yield ref;
        }
      }

      const connections = Object.values(view.connections);
      for (const { ref, id } of connections) {
        yield id;
        if (ref) {
          yield ref;
        }
      }
    }

    const mapping = new BidirectionalMultiMap<string, string>();

    for (const [id, view] of Object.entries(views)) {
      const refs = findReferencedConcepts(view);
      for (const ref of refs) {
        mapping.set(id, ref);
      }
    }

    const entitiesByViewId = fromEntries(
        iterate(mapping.mapping.associations())
      ),
      viewsByEntityId = fromEntries(iterate(mapping.inverse.associations()));

    this.update({
      description: 'New view reference mapping available',
      payload: {
        entitiesByViewId: entitiesByViewId as Dictionary<string[]>,
        viewsByEntityId: viewsByEntityId as Dictionary<string[]>,
      },
    });
  }

  @MonitorAsync('isBuildingEntityIndex')
  @ManagedTask('Indexing model entities', { isQuiet: true })
  private async buildModelEntityIndex(
    elements: Dictionary<ModelElement>,
    relations: Dictionary<ModelRelation>,
    views: Dictionary<ModelView>
  ) {
    function buildViewEntityIndex() {
      return {
        ...views.nodes,
        ...views.connections
      }
    }

    const entitiesById = {
      ...elements,
      ...relations,
      ...views,
      ...buildViewEntityIndex(),
    };

    this.update({
      description: 'New entities index available',
      payload: { entitiesById },
    });
  }
}
