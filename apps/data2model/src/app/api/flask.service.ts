import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ElementDefinition, ExtractorDatasetEntry, RelationshipDefinition, ViewDefinition } from "../extractor/extractor-types";
import { ApiModule } from './api.module';

export interface ExtractorResult {
  metadata: any[];
  model: any;
}

@Injectable({
  providedIn: ApiModule
})
export class FlaskService {
  public readonly basePath: string = 'flask';

  constructor(private http: HttpClient) {}

  public extract(
    data: ExtractorDatasetEntry[] = [],
    context: {
      elements?: ElementDefinition[];
      relations?: RelationshipDefinition[];
      views?: ViewDefinition[];
    } = {}
  ): Observable<ExtractorResult> {
    const path = `${this.basePath}/extract`;

    const body = {
      data: data,
      rules: context
    };

    return this.http.authorize().post<ExtractorResult>(path, body);
  }

  public parseDataset(file: File): Observable<ExtractorDatasetEntry[]> {
    const path = `${this.basePath}/parse_dataset`;

    const formParams = new FormData();

    // verify required parameter 'file' is not null or undefined
    if (file === null || file === undefined) {
      throw new Error(
        'Required parameter file was null or undefined when calling parseDataset.'
      );
    }

    formParams.append('file', file, file.name);

    return this.http
      .authorize()
      .post<ExtractorDatasetEntry[]>(path, formParams);
  }
}
