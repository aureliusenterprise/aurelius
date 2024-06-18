import { repositoryLogBasePath } from '../constants';
import { GetOptions, RepositoryVersion } from '../types';
import { getHttpClient } from '../utils';

/**
 * Retrieves the version string of the repository this application is currently connected to.
 * If the version string is unavailable for whatever reason, returns `unknown` instead.
 */
export function repositoryVersion({ forceUpdate }: GetOptions = {}) {
  const http = getHttpClient(),
    path = `${repositoryLogBasePath}/version`;

  return http.cache(forceUpdate).get<RepositoryVersion>(path);
}
