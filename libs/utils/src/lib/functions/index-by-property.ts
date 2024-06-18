import { Dictionary } from 'lodash';
import { SubType } from '../types';

/**
 * Returns a dictionary containing all rows of the given `data` indexed by property `propertyName`.
 * The keys referenced by `propertyName` should be unique (e.g. an id).
 * If duplicate index keys do exist, only the last found row is indexed.
 *
 * A common use case for this function is to create a lookup table of a dataset.
 *
 * @param data The data to index
 * @param propertyName The name of the property to index by
 */
export function indexByProperty<T extends Dictionary<any>>(
  data: Iterable<T>,
  propertyName: keyof SubType<T, string | number>
): Dictionary<T> {
  // Iterate over the dataset and add every row to the index keyed by its respective value for `propertyName`.
  const result: Dictionary<T> = {};
  for (const row of data) {
    result[row[propertyName as string | number]] = row;
  }
  return result;
}
