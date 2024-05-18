import { Injectable } from '@angular/core';
import {
  ClassificationDef,
  ClassificationDefAPIService
} from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { switchMap } from 'rxjs/operators';

export interface ClassificationStoreContext {
  readonly classificationType?: ClassificationDef;
  readonly classificationName?: string;
  readonly isRetrievingTypeDefinition?: boolean;
  readonly sources?: string[];
}

@Injectable()
export class ClassificationService extends BasicStore<ClassificationStoreContext> {
  constructor(
    private readonly classificationDefApiService: ClassificationDefAPIService
  ) {
    super();
    this.init();
  }

  private init() {
    this.select('classificationName')
      .pipe(
        switchMap((classificationName) =>
          this.handleRetrieveClassificationDef(classificationName)
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  set classificationName(classificationName: string) {
    this.update({
      description: 'New classification name available',
      payload: { classificationName },
    });
  }

  set sources(sources: string[]) {
    this.update({
      description: 'New sources available',
      payload: { sources },
    });
  }

  @ManagedTask('Retrieving the classification type definition', {
    isQuiet: true,
  })
  @MonitorAsync('isRetrievingTypeDefinition')
  private async handleRetrieveClassificationDef(classificationName: string) {
    const classificationType = await this.classificationDefApiService
      .getClassificationDefByName(classificationName)
      .toPromise();

    this.update({
      description: 'New classification type definition available',
      payload: { classificationType },
    });
  }
}
