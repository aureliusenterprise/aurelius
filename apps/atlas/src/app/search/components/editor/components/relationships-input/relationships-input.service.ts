import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { Observable } from 'rxjs';

export interface RelationshipsInputStoreContext {
  readonly relationships: string[];
  readonly typeName: string;
}
@Injectable()
export class RelationshipsInputService extends BasicStore<RelationshipsInputStoreContext> {
  readonly relationships$: Observable<string[]>;
  readonly typeName$: Observable<string>;

  constructor() {
    super();
    this.relationships$ = this.select('relationships');
    this.typeName$ = this.select('typeName');
  }

  set relationships(relationships: string[]) {
    this.update({
      description: 'New relationships available',
      payload: { relationships },
    });
  }

  set typeName(typeName: string) {
    this.update({
      description: 'New type name available',
      payload: { typeName },
    });
  }
}
