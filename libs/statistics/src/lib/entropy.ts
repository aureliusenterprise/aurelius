import { groupBy } from '@models4insight/utils';
import { Dictionary, sum } from 'lodash';

/**
 * Calculates the Shannon entropy over the given key(s) in the given dataset
 */
export async function entropy<T extends Dictionary<any>>(
  /** The dataset which to calculate the entropy over */
  data: T[],
  /** The key of the column(s) in the dataset which to calculate the entropy over */
  groupByColumn: keyof T | [...(keyof T)[]]
): Promise<number> {
  // By default, the entropy equals 0
  let result = 0;
  // Determine the lenght of the dataset
  const datasetLength = data.length;
  // If there is any data...
  if (datasetLength > 0) {
    // Calculate the entropy over the given key in the dataset
    result =
      -1 *
      sum(
        Object.values(groupBy(data, groupByColumn)).map(
          ({ length }) =>
            (length / datasetLength) * Math.log(length / datasetLength)
        )
      );
  }
  return result;
}
