import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { GetOptions } from '../../types';
import { getHttpClient } from '../elastic-api.module';

export interface ElasticSearchEntity {
  id: string;
  qualityguid_completeness: string;
  qualityguid_timeliness: string;
  dqscore_completeness: string;
  deriveddataset: string[];
  typename: string;
  dqscorecnt_uniqueness: string;
  referenceablequalifiedname: string;
  qualityguid_uniqueness: string;
  dqscorecnt_timeliness: string;
  deriveddataentity: string;
  dqscorecnt_accuracy: string;
  deriveddatasetguid: string[];
  supertypenames: string[];
  qualityguid_validity: string;
  guid: string;
  dqscore_validity: string;
  deriveddatadomainguid: string;
  derivedperson: string[];
  dqscore_timeliness: string;
  dqscorecnt_validity: string;
  dqscore_accuracy: string;
  m4isourcetype: string;
  deriveddatadomain: string;
  dqscorecnt_completeness: string;
  definition: string;
  name: string;
  sourcetype: string;
  qualityguid_accuracy: string;
  derivedpersonguid: string[];
  dqscore_uniqueness: string;
}

export function getAppSearchEntity(
  guid: string,
  { forceUpdate = false }: GetOptions = {}
): Observable<ElasticSearchEntity> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getAppSearchEntity');

  const path = `elastic/documents?ids%5B%5D=${guid}`;

  return http
    .cache(forceUpdate)
    .get<ElasticSearchEntity[]>(path)
    .pipe(map((result) => result?.[0]));
}
