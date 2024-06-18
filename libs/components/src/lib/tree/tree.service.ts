import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { switchMap } from 'rxjs/operators';
import { v4 as uuid } from 'uuid';
import { ManagedTask } from '@models4insight/task-manager';

export type Path = string | PathIndex;

export interface PathIndex {
  readonly [path: string]: Path;
}

export interface TreeLevel {
  readonly id: string;
  readonly name: string;
  readonly children?: TreeLevel[];
  readonly parent?: string;
  readonly value?: string;
}

export interface TreeStoreContext {
  readonly activeNode?: string;
  readonly isBuildingTree?: boolean;
  readonly nodesById?: Dictionary<TreeLevel>;
  readonly pathIndex?: PathIndex;
  readonly tree?: TreeLevel[];
}

@Injectable()
export class TreeService extends BasicStore<TreeStoreContext> {
  constructor() {
    super();
    this.init();
  }

  private init() {
    this.select('pathIndex')
      .pipe(
        switchMap((index) => this.handleBuildTree(index)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  @ManagedTask('Building the tree')
  @MonitorAsync('isBuildingTree')
  private async handleBuildTree(index: PathIndex) {
    const [topLevelNodesById, nodesById] = this.compileTreeLevel(index);

    const tree = Object.values(topLevelNodesById).sort((a, b) =>
      a.name.localeCompare(b.name)
    );

    this.update({
      description: 'New tree available',
      payload: {
        nodesById,
        tree,
      },
    });
  }

  private compileTreeLevel(
    index: PathIndex,
    nodesById: Dictionary<TreeLevel> = {},
    parent?: string
  ): [Dictionary<TreeLevel>, Dictionary<TreeLevel>] {
    const currentLevelNodesById: Dictionary<TreeLevel> = {};

    for (const [name, value] of Object.entries(index)) {
      // If value is a string, it represents a leaf. Otherwise, it represents a node with children.
      if (typeof value === 'string') {
        currentLevelNodesById[value] = {
          id: value,
          name,
          parent,
          value,
        };
      } else {
        const id = uuid();

        const [childrenById] = this.compileTreeLevel(value, nodesById, id);

        const children = Object.values(childrenById).sort((a, b) =>
          a.name.localeCompare(b.name)
        );

        currentLevelNodesById[id] = {
          children,
          id,
          name,
          parent,
        };
      }
    }

    for (const [id, node] of Object.entries(currentLevelNodesById)) {
      nodesById[id] = node;
    }

    return [currentLevelNodesById, nodesById];
  }
}
