import { Dictionary, omit } from 'lodash';
import { union } from './union';

/**
 * Returns a flattened representation of the given object
 */
export function flattenObject(
  /** The object to flatten */
  object: Dictionary<any>
) {
  let result = Object.assign({}, object);
  Object.keys(object).forEach((key) => {
    const property = object[key];
    if (typeof property === 'object') {
      result = omit(union(result, flattenObject(property)), key);
    }
  });
  return result;
}
