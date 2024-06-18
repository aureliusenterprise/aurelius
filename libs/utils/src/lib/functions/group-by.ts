import { Dictionary, groupBy as _groupBy } from 'lodash';

/**
 * Performs a group by operation on a dictionary based on one or multiple keys.
 * In the case of multiple keys, the resulting dictionary is indexed by a composite key delimited by # symbols.
 */
export function groupBy<T extends Dictionary<any>>(
  /** The dataset to group */
  data: T[],
  /** The keys to group by */
  keys: keyof T | [...(keyof T)[]]
): Dictionary<T[]> {
  // Harmonize the function inputs to always be an array
  if (!Array.isArray(keys)) {
    keys = [keys];
  }

  // Group the data by the given keys. If multiple keys are given, construct a composite key delimited by # symbols.
  return _groupBy(data, (item) =>
    (keys as (keyof T)[]).map((key) => item[key]).join('#')
  );
}
