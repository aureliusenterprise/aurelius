import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { EntityElementWithEXTInfo, GetOptions } from '../../types';
import { createHttpParams } from '../../utils';
import { getHttpClient } from '../atlas-api.module';

export type EntityAuditAction =
  | 'BUSINESS_ATTRIBUTE_UPDATE'
  | 'CLASSIFICATION_ADD'
  | 'CLASSIFICATION_DELETE'
  | 'CLASSIFICATION_UPDATE'
  | 'CUSTOM_ATTRIBUTE_UPDATE'
  | 'ENTITY_CREATE'
  | 'ENTITY_DELETE'
  | 'ENTITY_IMPORT_CREATE'
  | 'ENTITY_IMPORT_DELETE'
  | 'ENTITY_IMPORT_UPDATE'
  | 'ENTITY_PURGE'
  | 'ENTITY_UPDATE'
  | 'LABEL_ADD'
  | 'LABEL_DELETE'
  | 'PROPAGATED_CLASSIFICATION_ADD'
  | 'PROPAGATED_CLASSIFICATION_DELETE'
  | 'PROPAGATED_CLASSIFICATION_UPDATE'
  | 'TERM_ADD'
  | 'TERM_DELETE';

export interface EntityAuditEvent {
  readonly entityId: string;
  readonly timestamp: number;
  readonly user: string;
  readonly action: EntityAuditAction;
  readonly details: string;
  readonly eventKey: string;
  readonly entity?: EntityElementWithEXTInfo;
  readonly type?: string;
}

export interface GetEntityAuditOptions {
  readonly auditAction?: EntityAuditAction;
  readonly count?: number;
  readonly offset?: number;
  readonly sortBy?: string;
  readonly sortOrder?: 'ASC' | 'DESC';
  readonly startKey?: string;
}

/**
 * Retrieves the audit log for the entity with the given `guid` from the Atlas API
 */
export function getEntityAudit(
  /** The guid of the entity */
  guid: string,
  {
    count = 100,
    forceUpdate = false,
    offset = 0,
    sortOrder = 'DESC',
    ...options
  }: GetOptions & GetEntityAuditOptions = {}
): Observable<EntityAuditEvent[]> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getEntityAudit');

  const path = `atlas/v2/entity/${guid}/audit`;

  const queryParameters = createHttpParams({
    count,
    offset,
    sortOrder,
    ...options,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http.cache(forceUpdate).get<EntityAuditEvent[]>(path, requestOptions);
}
