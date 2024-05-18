import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { Subject } from 'rxjs';
import { exhaustMap } from 'rxjs/operators';
import { FlaskService } from '../../api/flask.service';
import { ExtractorService } from '../extractor.service';

export interface FileUploadStoreContext {
  readonly isParsingFile?: boolean;
}

@Injectable()
export class FileUploadService extends BasicStore<FileUploadStoreContext> {
  private onSubmit$: Subject<File> = new Subject<File>();

  constructor(
    private extractorService: ExtractorService,
    private flaskApi: FlaskService,
    private router: Router,
    storeService: StoreService
  ) {
    super({ name: 'FileUploadService', storeService });
    this.init();
  }

  private init() {
    // Whenever an upload is triggered, submit the current file to the API and return the parsed result.
    // Only one upload can be active at a time.
    // On a successful upload, navigate the user to the dataset page.
    this.onSubmit$.pipe(exhaustMap(file => this.handleParse(file))).subscribe();
  }

  submitFile(file: File) {
    this.onSubmit$.next(file);
  }

  @MonitorAsync('isParsingFile')
  @ManagedTask('Parsing the dataset')
  private async handleParse(file: File) {
    const dataset = await this.flaskApi.parseDataset(file).toPromise();

    this.extractorService.updateDataset(dataset);

    this.router.navigate(['home', 'dataset']);
  }
}
