import { Dictionary } from 'lodash';

/**
 * Builds a dictionary out of the given key-value pairs.
 *
 * @param entries The key-value pairs out of which to build the dictionary.
 */
export function fromEntries<K extends keyof Dictionary<V>, V>(
  entries: Iterable<[K, V]>
): Dictionary<V> {
  const result: Dictionary<V> = {};
  for (const [key, value] of entries) {
    result[key] = value;
  }
  return result;
}
