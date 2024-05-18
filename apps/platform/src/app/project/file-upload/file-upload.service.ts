import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';

export interface FileUploadStoreContext {
  isFileUploadFormSubmitted?: boolean;
}

export const fileUploadServiceDefaultState: FileUploadStoreContext = {
  isFileUploadFormSubmitted: false
};

@Injectable()
export class FileUploadService extends BasicStore<FileUploadStoreContext> {
  constructor(storeService: StoreService) {
    super({
      defaultState: fileUploadServiceDefaultState,
      name: 'FileUploadService',
      storeService
    });
  }
}
