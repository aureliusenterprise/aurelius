import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { getModel } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest } from 'rxjs';
import { debounceTime, filter, switchMap } from 'rxjs/operators';
import { ServicesModelModule } from './services-model.module';

export interface ModelStoreContext {
  readonly branch?: string;
  readonly isLoadingModel?: boolean;
  readonly model?: any;
  readonly version?: number;
}

@Injectable({
  providedIn: ServicesModelModule,
})
export class ModelService extends BasicStore<ModelStoreContext> {
  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({
      name: 'ModelService',
      storeService,
    });
    this.init();
  }

  private init() {
    this.projectService
      .select('projectId')
      .pipe(untilDestroyed(this))
      .subscribe(() => this.reset());

    combineLatest([
      this.select('branch', { includeFalsy: true }),
      this.select('version', { includeFalsy: true }),
    ])
      .pipe(
        debounceTime(50),
        filter(([branch]) => !!branch),
        switchMap(([branch, version]) =>
          this.handleRetrieveModel(branch, version)
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  set model(model: any) {
    this.update({
      description: 'New model available',
      payload: { model },
    });
  }

  @ManagedTask('Loading the model', { isQuiet: true })
  @MonitorAsync('isLoadingModel')
  private async handleRetrieveModel(branch: string, version: number) {
    const [{ project }, username] = await Promise.all([
      this.projectService.getCurrentProject(),
      this.authenticationService.get(['credentials', 'username']),
    ]);

    const model = await getModel(
      'archimate3',
      project,
      branch,
      '',
      'TRUNK',
      username,
      'json',
      { version }
    ).toPromise();

    this.model = model;
  }
}
