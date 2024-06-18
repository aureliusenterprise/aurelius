import { HttpResponse } from '@angular/common/http';
import { saveAs } from 'file-saver';
import { map } from 'rxjs/operators';
import { getModel } from '../get-model';
import { GetOptions, ModelCommitContentTypeEnum } from '../types';

export interface DownloadModelOptions {
  /** The format in which the model should be retrieved */
  contentType?: ModelCommitContentTypeEnum;
  /** The ID of the model which to retrieve */
  modelId?: string;
  /** The ID of the module which to retrieve */
  module?: string;
  /** The name of the parser to use */
  parserName?: 'archimate3';
}

export const defaultDownloadModelOptions: DownloadModelOptions = {
  contentType: ModelCommitContentTypeEnum.ARCHIMATE,
  module: '',
  modelId: 'TRUNK',
  parserName: 'archimate3',
};

function findFileName(response: HttpResponse<any>) {
  const contentDisposition = response.headers.get('content-disposition') || '';
  const matches = /filename=([^;]+)/gi.exec(contentDisposition);
  return (matches[1] || '').trim();
}

/**
 * Download a version of a model from the given project and branch in a particular format
 */
export function downloadModel(
  /** The full name of the project from which to retrieve the model */
  fullProjectName: string,
  /** The name of the branch from which to retrieve the model */
  branch: string,
  /** The username of the user downloading the model */
  userid: string,
  /** */
  version?: number,
  /** Additional parameters for the download model operation */
  options: DownloadModelOptions & GetOptions = defaultDownloadModelOptions
) {
  const { contentType, forceUpdate, modelId, module, parserName } = {
    ...defaultDownloadModelOptions,
    ...options,
  };

  return getModel(
    parserName,
    fullProjectName,
    branch,
    module,
    modelId,
    userid,
    contentType,
    { forceUpdate, observe: 'response', responseType: 'text', version }
  ).pipe(
    map((response: HttpResponse<string>) => {
      saveAs(
        new Blob([response.body], {
          type: contentType === 'json' ? 'application/json' : 'text/xml',
        }),
        findFileName(response)
      );
    })
  );
}
