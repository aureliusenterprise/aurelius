import { Dictionary } from 'lodash';
import { fromEntries } from './from-entries';

function* parseQueryParams(queryParams: string[]): Generator<[string, string]> {
  for (const queryParam of queryParams) {
    const [key, value] = queryParam.split('=') as [string, string];

    if (typeof value !== 'string')
      throw new Error('Query param string is not correctly formatted');

    yield [decodeURIComponent(key), decodeURIComponent(value)];
  }
}

/**
 * Finds the query parameters from the given `url` and returns them as a dictionary of key-value pairs
 *
 * @param url The URI string from which to get the query parameters
 */
export function getQueryParametersFromUrl(url: string): Dictionary<string> {
  if (!url) return {};

  const [, params] = url.split('?');

  if (!params?.length) return {};

  const queryParamString = params.split('#')[0];

  if (!queryParamString?.length) return {};

  const queryParams = queryParamString.split('&');

  const parsedQueryParams = parseQueryParams(queryParams);

  return fromEntries(parsedQueryParams);
}
