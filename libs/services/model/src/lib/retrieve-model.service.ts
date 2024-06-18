import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  downloadModel,
  ModelCommitContentTypeEnum,
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Subject } from 'rxjs';
import { exhaustMap } from 'rxjs/operators';
import { ServicesModelModule } from './services-model.module';

interface RetrieveModelContext {
  readonly branchId: string;
  readonly contentType: ModelCommitContentTypeEnum;
  readonly version?: number;
}

export interface RetrieveModelStoreContext {
  readonly isRetrievingModel?: boolean;
}

export const defaultRetrieveModelServiceState: RetrieveModelStoreContext = {
  isRetrievingModel: false,
};

@Injectable({
  providedIn: ServicesModelModule,
})
export class RetrieveModelService extends BasicStore<RetrieveModelStoreContext> {
  private readonly onModelRetrieved$ = new Subject<void>();
  private readonly retrieveModel$ = new Subject<RetrieveModelContext>();

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultRetrieveModelServiceState,
      name: 'RetrieveModelService',
      storeService,
    });
    this.init();
  }

  private init() {
    // Whenever a retrieve model is triggered, handle the retrieve. Only one retrieve can be active at a time.
    this.retrieveModel$
      .pipe(
        exhaustMap(({ branchId, contentType, version }) =>
          this.handleRetrieveModel(branchId, contentType, version)
        ),
        untilDestroyed(this)
      )
      .subscribe(this.onModelRetrieved$);
  }

  retrieveModel(
    branchId: string,
    contentType: ModelCommitContentTypeEnum,
    version?: number
  ) {
    this.retrieveModel$.next({
      branchId,
      contentType,
      version,
    });
  }

  get onModelRetrieved() {
    return this.onModelRetrieved$.asObservable();
  }

  @ManagedTask('Retrieving the model from the repository')
  @MonitorAsync('isRetrievingModel')
  private async handleRetrieveModel(
    branchId: string,
    contentType: ModelCommitContentTypeEnum,
    version: number
  ) {
    const [{ project }, username] = await Promise.all([
      this.projectService.getCurrentProject(),
      this.authenticationService.get(['credentials', 'username']),
    ]);

    return downloadModel(project, branchId, username, version, {
      contentType,
    }).toPromise();
  }
}
